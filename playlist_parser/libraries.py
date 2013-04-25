#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

import os
import logging
from xdg.BaseDirectory import xdg_data_home

from playlist_parser import playlists, utils

logger = logging.getLogger(__name__)


class Library(object):

	def __init__(self):
		logging.info('Creating Library')
		self.playlists = []

	def copy(self, dst):
		logger.info('Copying %r to %s' % (self, dst))
		for playlist in self.playlists:
			playlist.copy(dst)


class RhythmboxLibrary(Library, utils.XmlParser):

	def __init__(self, rhythmbox_file=None):
		self.current_playlist = None
		if not rhythmbox_file:
			rhythmbox_file = os.path.join(xdg_data_home,
					'rhythmbox', 'playlists.xml')
		Library.__init__(self)
		utils.XmlParser.__init__(self, rhythmbox_file)

	def parsing_start_element(self, tag, attrs):
		if self.current_tag == "playlist" and attrs['type'] == "static":
			self.current_playlist = playlists.RhythmboxPlaylist(
					attrs['name'], encoding=self.encoding)

	def parsing_char_data(self, data):
		if self.current_tag == "location":
			if self.current_playlist == None:
				logger.error('[ERROR] No playlist to put "%s"' % data)
				return
			self.current_playlist.add_file(data)

	def parsing_end_element(self, tag):
		if tag == "playlist" and self.current_playlist is not None:
			self.playlists.append(self.current_playlist)
			logger.info(repr(self.current_playlist))
			self.current_playlist = None
