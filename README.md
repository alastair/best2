# Best #

Best reads a collection of music files and generates a playlist based on
the top 2 tracks ranked on last.fm for each artist. Best can currently read
mp3, flac and ogg files.  Files must be renamed with musicbrainz artist id
tags.

### Requirements ###
* python-sqlite3
* pylast - http://code.google.com/p/pylast/
* albumidentify - http://github.com/scottr/albumidentify
* A last.fm API key

### Running ###
Put your last.fm key in best.py, then run:
    $ ./best.py import ~/music
    $ ./best.py download
    $ ./best.py generate > playlist.m3u
