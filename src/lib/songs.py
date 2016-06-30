import re
import shutil
import os.path
import logging

from lib.utils import to_fat_compat

logger = logging.getLogger(__name__)


class Song:

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

    def copy(self, folder_dst, track_number=None):
        file_dst = os.path.basename(self.location)
        folder_dst = to_fat_compat(folder_dst)
        if track_number is not None:
            if re.match("^[0-9]+\W*-?\W*", file_dst):
                file_dst = re.sub("^[0-9]+\W*-?\W*", track_number, file_dst)
            else:
                file_dst = track_number + file_dst
        file_dst = to_fat_compat(os.path.join(folder_dst, file_dst))
        if os.path.exists(file_dst):
            logger.debug('Song %r already here', self)
            return self.__class__(file_dst, self.title, self.encoding)
        if not os.path.exists(folder_dst):
            os.makedirs(folder_dst, exist_ok=True)

        try:
            logger.warn('Writing %s', file_dst)
            shutil.copy(self.location, file_dst)
        except Exception as error:
            logger.exception(error)
            return None
        return self.__class__(file_dst, self.title, self.encoding)

    def __str__(self):
        if self.title is not None:
            return self.title.encode(self.encoding)
        return 'song'

    def __repr__(self):
        return r'<Song %r>' % self.title

# vim: set et sts=4 sw=4 tw=120:
