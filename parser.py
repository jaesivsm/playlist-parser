#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

import shutil
import urllib
import os.path
import xml.parsers.expat

class Song(object):

	def __init__(self, path):
		self.path = path
		self.name = self.__name_me(self.path)

	def __name_me(self, path):
		return path.split('/')[-1]

	def complete_path(self, path):
		self.path += path
		self.name = self.__name_me(self.path)

	def copy(self, dst):
		file_name = self.path[7:]
		if os.path.exists(os.path.join(dst, os.path.basename(file_name))):
			print(u'Song %r already here' % self)
			return
		if not os.path.exists(dst):
			print("Creating directory %r" % dst)
			try:
				os.mkdir(dst)
			except OSError, error:
				if error.errno != 17:
					raise
		try:
			print(u'Copying %r to %s' % (self, dst))
			shutil.copy(self.path[7:], dst)
		except Exception, error:
			print error
			pass

	def __str__(self):
		return self.name.encode('utf8')
	def __repr__(self):
		return r'<Song %r>' % self.name

class Playlist(object):

	def __init__(self, attrs):
		self.name = attrs['name']
		self.automatic = True if attrs['type'] == u"automatic" else False
		self.songs = []

	def add_file(self, path):
		if path.startswith('file://'):
			self.songs.append(Song(path))
		else:
			self.songs[-1].complete_path(path)

	def copy(self, dst):
		print('Copying %r to %s' % (self, dst))
		dst = os.path.join(dst, self.name)
		for i, song in enumerate(self.songs):
			song.copy(dst)

	def __str__(self):
		return self.name.encode('utf8')
	def __repr__(self):
		return r'<Playlist %r>' % self.name

class Library(object):

	def __init__(self, playlist_xml=None):
		self.playlists = []
		self.current_playlist = None
		self.previous_state = []
		self.state = None
		self.parser = xml.parsers.expat.ParserCreate()

		self.parser.StartElementHandler = self.parsing_start_element
		self.parser.EndElementHandler = self.parsing_end_element
		self.parser.CharacterDataHandler = self.parsing_char_data

		if playlist_xml:
			self.parse(playlist_xml)

	def parse(self, playlists_xml='playlists.xml'):
		try:
			playlist_fd = open(playlists_xml, 'r')
		except IOError:
			print("[ERROR] Could't load file")
			return False
		self.parser.Parse(urllib.unquote(playlist_fd.read()))

	def copy(self, dst):
		print('Copying %r to %s' % (self, dst))
		for playlist in self.playlists:
			playlist.copy(dst)

	def parsing_start_element(self, name, attrs):
		self.previous_state.append(self.state)
		self.state = name
		if name == "playlist" and attrs['type'] == "static":
			self.current_playlist = Playlist(attrs)
			print('[%s] %s "%s"' % (len(self.playlists),
					"Creating playlist", self.current_playlist.name))

	def parsing_char_data(self, data):
		if self.state == "location":
			if self.current_playlist == None:
				print('[ERROR] No playlist to put "%s"' % data)
				return
			self.current_playlist.add_file(data)

	def parsing_end_element(self, name):
		self.state = self.previous_state.pop()
		if name == "playlist" and self.current_playlist is not None:
			self.playlists.append(self.current_playlist)
			print("\tAdded %s songs to the playlist"
					% len(self.current_playlist.songs))
			self.current_playlist = None
