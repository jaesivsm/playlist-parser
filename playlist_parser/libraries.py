#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

import os
import urllib
import logging
import xml.parsers.expat
from xdg.BaseDirectory import xdg_data_home

from playlist_parser import playlists

logger = logging.getLogger(__name__)


class Library(object):

	def __init__(self, playlist_path=None):
		logging.info('Creating Library from file %r' % playlist_path)
		self.playlists = []
		self.playlist_path = playlist_path
		self.current_playlist = None
		self.previous_state = []
		self.state = None

		if self.playlist_path:
			self.parse(self.playlist_path)

	def parse(self):
		raise NotImplementedError()

	def copy(self, dst):
		logger.info('Copying %r to %s' % (self, dst))
		for playlist in self.playlists:
			playlist.copy(dst)


class RhythmboxLibrary(Library):

	def __init__(self, playlist_path=None):
		self.parser = xml.parsers.expat.ParserCreate()

		self.parser.StartElementHandler = self.__parsing_start_element
		self.parser.EndElementHandler = self.__parsing_end_element
		self.parser.CharacterDataHandler = self.__parsing_char_data

		if not playlist_path:
			playlist_path = os.path.join(xdg_data_home,
					'rhythmbox', 'playlists.xml')
		Library.__init__(self, playlist_path)

	def parse(self, playlists_xml='playlists.xml'):
		with open(playlists_xml, 'r') as playlist_fd:
			self.parser.Parse(urllib.unquote(playlist_fd.read()))

	def __parsing_start_element(self, name, attrs):
		self.previous_state.append(self.state)
		self.state = name
		if name == "playlist" and attrs['type'] == "static":
			self.current_playlist = playlists.RhythmboxPlaylist(attrs['name'])

	def __parsing_char_data(self, data):
		if self.state == "location":
			if self.current_playlist == None:
				logger.error('[ERROR] No playlist to put "%s"' % data)
				return
			self.current_playlist.add_file(data)

	def __parsing_end_element(self, name):
		self.state = self.previous_state.pop()
		if name == "playlist" and self.current_playlist is not None:
			self.playlists.append(self.current_playlist)
			logger.info(repr(self.current_playlist))
			self.current_playlist = None
