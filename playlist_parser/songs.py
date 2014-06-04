import shutil
import os.path
import logging

from playlist_parser.utils import to_fat_compat

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

    def copy(self, folder_dst):
        file_dst = to_fat_compat(os.path.join(folder_dst,
                                              os.path.basename(self.location)))
        if os.path.exists(file_dst):
            logger.info('Song %r already here' % self)
            return
        if not os.path.exists(folder_dst):
            logger.info("Creating directory %r" % folder_dst)
            try:
                os.mkdir(folder_dst)
            except OSError as error:
                if error.errno != 17:  # file already exists
                    raise
        try:
            logger.info('Copying %r to %s' % (self, file_dst))
            shutil.copy(self.location, file_dst)
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
