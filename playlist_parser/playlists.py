#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

import os.path

from playlist_parser import songs


class Playlist(object):

	def __init__(self, name):
		self.name = name
		self.songs = []

	def add_file(self, path):
		self.songs.append(Song(path))

	def copy(self, dst):
		print('Copying %r to %s' % (self, dst))
		dst = os.path.join(dst, self.name)
		for i, song in enumerate(self.songs):
			song.copy(dst)

	def __str__(self):
		return self.name.encode('utf8')
	def __repr__(self):
		return r'<Playlist %r>' % self.name


class RhythmboxPlaylist(Playlist):

	def add_file(self, path):
		if path.startswith('file://'):
			self.songs.append(songs.RhythmboxSong(path[7:]))
		else:
			self.songs[-1].complete_path(path)
