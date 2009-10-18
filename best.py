#!/usr/bin/python2.5

import sys
import os
sys.path.insert(0, os.path.expanduser("~/Projects/albumidentify"))
import sqlite3
import tag
import time
import lastfm


class Best:
	def __init__(self):
		self.conn = sqlite3.connect("best.db")

	def best(self):
		artists = self.conn.cursor()
		artists.execute("select distinct artist_id from top")
		for row in artists:
			#print "artist",row[0]
			songs = self.conn.cursor()
			songs.execute("select title from top where artist_id=? order by rank limit 0,2", (row[0],))
			for row2 in songs:
				#print "  * song",row2[0]
				best = self.conn.cursor()
				sql = "select filename from best where artist_id=? and lower(track) like ? \
						order by year limit 0,1"
				# Could do more matching here - Rank greatest hits/live releases lower
				# Also do partial matching and matching without puncuation
				best.execute(sql, (row[0], row2[0].lower()))
				for row3 in best:
					print row3[0]

class Download:
	def __init__(self, delete=False):
		self.conn = sqlite3.connect("best.db")
		self.create_db()
		if delete:
			self.conn.execute("delete from top")
			self.conn.commit()

	def create_db(self):
		sql = "CREATE TABLE IF NOT EXISTS top ( \
				artist varchar(255), \
				artist_id varchar(50),\
				rank int,\
				title varchar(50))"
		self.conn.execute(sql)
		self.conn.execute("CREATE INDEX IF NOT EXISTS artist_id_idx on top(artist_id)")

	def download(self, artist_id=None):
		c = self.conn.cursor()
		if artist_id is None:
			sql = "select distinct artist from best"
			c.execute(sql)
		else:
			sql = "select distinct artist from best where artist_id=?"
			c.execute(sql, (artist_id,))
		for artist in c:
			time.sleep(.5)
			print artist[0]
			rank = 1
			try:
				ts = lastfm.get_artist_toptracks(artist[0])
			except:
				print " * Error download for artist, skipping"
				continue
			for track in ts['track'][:10]:
				trname = track['name'][0]
				mbid = track['artist'][0]['mbid'][0]
				#print "*",trname,mbid
				sql = "insert into top (artist, artist_id, rank, title) values (?, ?, ?, ?)"
				self.conn.execute(sql, (artist[0], mbid, rank, trname))
				rank += 1
			self.conn.commit()

class Import:
	def __init__(self, delete=False):
		self.conn = sqlite3.connect("best.db")
		self.conn.text_factory = str
		self.create_db()
		if delete:
			self.conn.execute("delete from best")
			self.conn.commit()

	def create_db(self):
		sql = "CREATE TABLE IF NOT EXISTS best ( \
				artist varchar(255), \
				release varchar(255),\
				track varchar(255),\
				year varchar(4),\
				artist_id varchar(50),\
				release_id varchar(50),\
				track_id varchar(50),\
				filename varchar(255))"
		self.conn.execute(sql)
		self.conn.execute("CREATE INDEX IF NOT EXISTS artist_id_idx on best(artist_id)")
		self.conn.execute("CREATE INDEX IF NOT EXISTS track_name on best(track)")

	def import_all(self, dirs):
		for dir in dirs:
			self.import_dir(dir)

	def import_dir(self, dirname):
		"""Import a directory.  If the first item in this directory is a file
		then it is assumed that the directory is a single album.  Otherwise,
		directories are recursively scanned"""
		print "importing",dirname
		dir = os.listdir(dirname)
		for file in dir:
			fullpath = os.path.join(dirname,file)
			if os.path.isdir(fullpath):
				self.import_dir(fullpath)

			elif os.path.splitext(fullpath)[1].lower() in tag.supported_extensions:
				tags = tag.read_tags(fullpath)
				sql = "insert into best values (?,?,?,?,?,?,?,?)"
				args = self.get_args(tags, fullpath)
				self.conn.execute(sql, args)

		self.conn.commit()

	def get_args(self, tags, fullpath):
		return (
			self.get_single_tag(tags, tag.ARTIST),
			self.get_single_tag(tags, tag.ALBUM),
			self.get_single_tag(tags, tag.TITLE),
			self.get_single_tag(tags, tag.YEAR),
			self.get_single_tag(tags, tag.ARTIST_ID),
			self.get_single_tag(tags, tag.ALBUM_ID),
			self.get_single_tag(tags, tag.TRACK_ID),
			fullpath
		)

	def get_single_tag(self, tags, name):
		if type(tags[name]) == type([]):
			return tags[name][0]
		else:
			return tags[name]

def usage():
	print "usage: %s operation [-d] [dirs...]" % sys.argv[0]
	print "operation: 'import', 'download' or 'generate'"
	print "-d: delete db before import or download"
	print "only provide dirs on import"


if __name__ == '__main__':
	if len(sys.argv) < 2:
		usage()
		sys.exit(1)
	if sys.argv[1] == "import":
		if sys.argv[2] == "-d":
			delete = True
			args = sys.argv[3:]
		else:
			delete = False
			args = sys.argv[2:]
		Import(delete).import_all(args)
	elif sys.argv[1] == "download":
		if len(sys.argv) > 2 and sys.argv[2] == "-d":
			delete = True
		else:
			delete = False
		if len(sys.argv) == 4:
			Download(delete).download(sys.argv[3])
		else:
			Download(delete).download()
	elif sys.argv[1] == "generate":
		if len(sys.argv) == 3:
			Best().best(sys.argv[2])
		else:
			Best().best()
	else:
		usage()
