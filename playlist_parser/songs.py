#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

import shutil
import os.path

class Song(object):

	def __init__(self, path):
		self.path = path
		self.name = os.path.basename(path)

	def copy(self, dst):
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
			shutil.copy(self.path, dst)
		except Exception, error:
			print error
			pass

	def __str__(self):
		return self.name.encode('utf8')
	def __repr__(self):
		return r'<Song %r>' % self.name


class RhythmboxSong(Song):

	def complete_path(self, path):
		self.path += path
		self.name = os.path.basename(self.path)
