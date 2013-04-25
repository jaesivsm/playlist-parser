#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

import os.path
import urllib
import xml.parsers.expat

from playlist_parser import playlists


class Library(object):

	def __init__(self, playlist_file=None):
		self.playlists = []
		self.playlist_file = playlist_file
		self.current_playlist = None
		self.previous_state = []
		self.state = None

		if self.playlist_file:
			self.parse(self.playlist_file)

	def parse(self):
		raise NotImplementedError()

	def copy(self, dst):
		print('Copying %r to %s' % (self, dst))
		for playlist in self.playlists:
			playlist.copy(dst)


class RhythmboxLibrary(Library):

	def __init__(self, xml=None):
		self.playlist_file = xml
		self.parser = xml.parsers.expat.ParserCreate()

		self.parser.StartElementHandler = self.__parsing_start_element
		self.parser.EndElementHandler = self.__parsing_end_element
		self.parser.CharacterDataHandler = self.__parsing_char_data

		super(Library, self).__init__()

	def parse(self, playlists_xml='playlists.xml'):
		with open(playlists_xml, 'r') as playlist_fd:
			self.parser.Parse(urllib.unquote(playlist_fd.read()))

	def __parsing_start_element(self, name, attrs):
		self.previous_state.append(self.state)
		self.state = name
		if name == "playlist" and attrs['type'] == "static":
			self.current_playlist = playlists.RhythmboxPlaylist(attrs['name'])
			print('[%s] %s "%s"' % (len(self.playlists),
					"Creating playlist", self.current_playlist.name))

	def __parsing_char_data(self, data):
		if self.state == "location":
			if self.current_playlist == None:
				print('[ERROR] No playlist to put "%s"' % data)
				return
			self.current_playlist.add_file(data)

	def __parsing_end_element(self, name):
		self.state = self.previous_state.pop()
		if name == "playlist" and self.current_playlist is not None:
			self.playlists.append(self.current_playlist)
			print("\tAdded %s songs to the playlist"
					% len(self.current_playlist.songs))
			self.current_playlist = None
