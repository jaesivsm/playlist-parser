#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

import os.path
import logging

from playlist_parser import songs, utils

logger = logging.getLogger(__name__)


class Playlist(object):

	def __init__(self, name=None, encoding='UTF8'):
		logger.info(u'Creating playlist %s' % name)
		self.name = name
		self.songs = []
		self.encoding = encoding

	def add_song(self, song):
		self.songs.append(song)

	def add_file(self, path):
		self.songs.append(songs.Song(path))

	def copy(self, dst):
		logger.info('Copying %r to %s' % (self, dst))
		dst = os.path.join(dst, self.name)
		for i, song in enumerate(self.songs):
			song.copy(dst)

	def __str__(self):
		return self.name.encode(self.encoding)
	def __repr__(self):
		return r'Playlist %r contains %d songs' % (self.name, len(self.songs))


class RhythmboxPlaylist(Playlist):

	def add_file(self, path):
		if path.startswith('file://'):
			self.songs.append(songs.Song(path[7:]))
		else:
			self.songs[-1].__init__(self.songs[-1].path + path)

class PlsPlaylist(Playlist, utils.XmlParser):

	def __init__(self, playlist_path):
		self.current_song = None
		Playlist.__init__(self, os.path.basename(playlist_path))
		utils.XmlParser.__init__(self, playlist_path)

	def parsing_start_element(self, tag, attrs):
		if tag == "track":
			self.current_song = songs.Song()

	def parsing_char_data(self, data):
		if "track" in self.previous_tags and self.current_song is not None:
			setattr(self.current_song, self.current_tag, data)

	def parsing_end_element(self, tag):
		if tag == "track" and self.current_song is not None:
			self.add_song(self.current_song)
			logger.info(repr(self.current_song))
			self.current_song = None
