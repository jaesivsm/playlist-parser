import shutil
import os.path
import logging

logger = logging.getLogger(__name__)


class Song(object):

    def __init__(self, location=None, title=None, encoding='UTF8'):
        self.title = title
        self.encoding = encoding
        self.location = location
        self.length = None
        self.creator = None
        if self.location is not None and self.title is None:
            self.set_title()

    def set_title(self):
        self.title = os.path.splitext(os.path.basename(self.location))[0]

    def copy(self, dst):
        if os.path.exists(os.path.join(dst, os.path.basename(self.location))):
            logger.info('Song %r already here' % self)
            return
        if not os.path.exists(dst):
            logger.info("Creating directory %r" % dst)
            try:
                os.mkdir(dst)
            except OSError as error:
                if error.errno != 17:  # file already exists
                    raise
        try:
            logger.info('Copying %r to %s' % (self, dst))
            shutil.copy(self.location, dst)
        except Exception as error:
            logger.exception(error)
            pass

    def __str__(self):
        if self.title is not None:
            return self.title.encode(self.encoding)
        return 'song'
    def __repr__(self):
        return r'<Song %r>' % self.title

# vim: set et sts=4 sw=4 tw=120:
