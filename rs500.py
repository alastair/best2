#!/usr/bin/python2.5

import sys
import os
sys.path.insert(0, os.path.expanduser("~/Projects/albumidentify"))
import sqlite3
import tag
import time
import lastfm
import codecs

conn = sqlite3.connect("best.db")
def main(file):
	for line in codecs.open(file, encoding='utf-8'):
		parts = line.split("\t")
		track = parts[0].strip()
		artist = parts[1].strip()
		#print track.strip()
		best = conn.cursor()
		#print unicode(artist),unicode(track)
		sql = "select filename from best where lower(artist) = ? and lower(track) = ? \
			order by year limit 0,1"
		args = (artist.lower(), track.lower())
		#print args
		best.execute(sql, args)
		for row3 in best:
			print row3[0].encode("utf8")

if __name__ == "__main__":
	main(sys.argv[1])
