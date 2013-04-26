#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

import shutil
import os.path
import logging

logger = logging.getLogger(__name__)


class Song(object):

    def __init__(self, location=None, title=None, encoding='UTF8'):
        self.title = title
        self.encoding = encoding
        self.location = location
        if self.location is not None and self.title is None:
            self.title = os.path.basename(location)

    def copy(self, dst):
        if os.path.exists(os.path.join(dst, os.path.basename(self.location))):
            logger.info(u'Song %r already here' % self)
            return
        if not os.path.exists(dst):
            logger.info("Creating directory %r" % dst)
            try:
                os.mkdir(dst)
            except OSError, error:
                if error.errno != 17:
                    raise
        try:
            logger.info(u'Copying %r to %s' % (self, dst))
            shutil.copy(self.location, dst)
        except Exception, error:
            logger.exception(error)
            pass

    def __str__(self):
        if self.title is not None:
            return self.title.encode(self.encoding)
        return 'song'
    def __repr__(self):
        return r'<Song %r>' % self.title

# vim: set et sts=4 sw=4 tw=120:
