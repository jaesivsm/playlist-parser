#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

import os.path
import logging

from playlist_parser import utils
from playlist_parser.songs import Song

logger = logging.getLogger(__name__)


class Playlist(object):

	def __init__(self, name=None, encoding='UTF8'):
		logger.info(u'Creating playlist %s' % name)
		self.name = name
		self.songs = []
		self.encoding = encoding

	def add_song(self, song):
		logger.info(repr(song))
		self.songs.append(song)

	def add_file(self, path):
		self.songs.append(Song(path))

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
			self.add_song(Song(path[7:]))
		else:
			self.songs[-1].__init__(self.songs[-1].path + path)


class FilePlaylist(Playlist):

	def __init__(self, path):
		Playlist.__init__(self, os.path.basename(path))

		self.path = path
		self.directory = os.path.dirname(path)
		self.path_is_absolute = True if path.startswith('/') else False

	def get_abs_path(self, path):
		if path.startswith('/') or not self.path_is_absolute:
			return path
		return os.path.join(self.directory, path)


class PlsPlaylist(FilePlaylist, utils.XmlParser):

	def __init__(self, playlist_path):
		FilePlaylist.__init__(self, playlist_path)
		utils.XmlParser.__init__(self, playlist_path)

		self.current_song = None

	def parsing_start_element(self, tag, attrs):
		if tag == "track":
			self.current_song = Song(encoding=self.encoding)

	def parsing_char_data(self, data):
		if "track" in self.previous_tags and self.current_song is not None:
			if self.current_tag == "location":
				data = self.get_abs_path(data)
			setattr(self.current_song, self.current_tag, data)

	def parsing_end_element(self, tag):
		if tag == "track" and self.current_song is not None:
			self.add_song(self.current_song)
			self.current_song = None


class M3uPlaylist(FilePlaylist):

	def __init__(self, playlist_path):
		FilePlaylist.__init__(self, playlist_path)

		self.current_song = None
		if playlist_path:
			self.read(playlist_path)

	def read(self, path):
		logger.info('Parsing %s' % path)
		with open(path, 'r') as fd:
			lines = fd.xreadlines()
			for line in lines:
				logger.debug("Parsing %r" % line)
				if line.startswith('#EXTINF:'):
					line = line.strip()[8:]
					length = creator = title = location = None
					if ',' in line:
						length, line = line.split(',', 1)
					if ' - ' in line:
						creator, title = line.split(' -' )
					do_not_add = False
					while not location:
						location = self.get_abs_path(lines.next().strip())
						if os.path.exists(location):
							break
						elif location.startswith('#EXT'):
							do_not_add = True
							break
						else:
							logger.warn('File not found %r in playlist %r'
									% (location, path))
							location = None
					if do_not_add:
						continue
					song = Song(location, title)
					if creator is not None:
						song.creator = creator
					self.add_song(song)
				elif line.startswith('#EXTM3U'):
					continue
				else:
					if os.path.exists(line):
						self.add_file(line)
					else:
						logger.warn('File not found %r in playlist %r'
								% (line, path))


