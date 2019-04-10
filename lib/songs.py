import re
import shutil
import os.path
import logging

from lib.utils import to_fat_compat

import taglib

logger = logging.getLogger(__name__)
NUMBERED_TRACK = re.compile(r'^[0-9]+\W*-?\W*')


class Song:

    def __init__(self, location=None, encoding='UTF8'):
        self.encoding = encoding
        self.location = location
        self.__props = {'length': -1}
        self.__song_file = None

    def __dynamic_props_getter(self, prop_name, *tag_names):
        if self.__props.get(prop_name):
            return self.__props[prop_name]
        if not self.location:
            return ''
        if self.song_file:
            for tag_name in tag_names:
                if self.song_file and self.song_file.tags.get(tag_name):
                    self.__props[prop_name] = self.song_file.tags[tag_name][0]
                    break
        return self.__props.get(prop_name, '')

    def __dynamic_props_setter(self, prop_name, tag_name, value):
        if getattr(self, prop_name) and self.song_file:
            return  # won't override proper value, not a tag editor
        self.__props[prop_name] = value
        if self.song_file:
            self.song_file.tags[tag_name] = [value]
            self.song_file.save()

    @property
    def song_file(self):
        if taglib is not None and self.location and self.__song_file is None \
                and os.path.exists(self.location):
            self.__song_file = taglib.File(self.location)
        return self.__song_file

    @property
    def title(self):
        title = self.__dynamic_props_getter('title', 'TITLE')
        if self.location and not title:
            title = os.path.splitext(os.path.basename(self.location))[0]
            self.__props['title'] = title
        return title

    @title.setter
    def title(self, value):
        self.__dynamic_props_setter('title', 'TITLE', value)

    @property
    def artist(self):
        return self.__dynamic_props_getter('artist', 'ARTIST', 'ALBUMARTIST')

    @artist.setter
    def artist(self, value):
        self.__dynamic_props_setter('artist', 'ARTIST', value)

    @property
    def length(self):
        if self.song_file is not None:
            self.__props['length'] = self.song_file.length
        return self.__props['length']

    @length.setter
    def length(self, value):
        if self.length == -1:
            self.__props['length'] = value

    def copy(self, folder_dst, track_number=None):
        file_dst = os.path.basename(self.location)
        folder_dst = to_fat_compat(folder_dst)
        if track_number is not None:
            if NUMBERED_TRACK.match(file_dst):
                file_dst = NUMBERED_TRACK.sub(track_number, file_dst)
            else:
                file_dst = track_number + file_dst
        file_dst = to_fat_compat(os.path.join(folder_dst, file_dst))
        if os.path.exists(file_dst):
            logger.debug('Song %r already here', self)
            return self.__class__(file_dst, self.encoding)
        if not os.path.exists(folder_dst):
            os.makedirs(folder_dst, exist_ok=True)

        try:
            logger.warning('Writing %s', file_dst)
            shutil.copy(self.location, file_dst)
        except Exception as error:
            logger.exception(error)
            return None
        return self.__class__(file_dst, self.encoding)

    def __str__(self):
        if self.title is not None:
            return self.title.encode(self.encoding)
        return 'song'

    def __repr__(self):
        return r'<Song %r>' % self.title
