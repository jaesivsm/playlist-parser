import os
import logging
import urllib.parse
from lib import playlists
from lxml import etree

logger = logging.getLogger(__name__)


class Library:

    def __init__(self):
        self.playlists = []

    def __iter__(self):
        return iter(self.playlists)

    def __getitem__(self, key):
        return self.playlists[key]

    def append(self, playlist):
        return self.playlists.append(playlist)

    @property
    def current_playlist(self):
        return self.playlists[-1] if self.playlists else None

    def copy(self, dst):
        new_lib = Library()
        logger.info('Copying %r to %s', self, dst)
        for playlist in self:
            new_lib.playlists.append(playlist.copy(dst))
        return new_lib

    def export(self, dst, new_root):
        new_lib = Library()
        logger.info('Exporting library %r => %r', dst, new_root)
        for playlist in self:
            new_lib.playlists.append(playlist.export(dst, new_root))
        return new_lib


class RhythmboxLibrary(Library):

    def __init__(self, rhythmbox_file=None):
        super().__init__()
        if not rhythmbox_file:
            rhythmbox_file = os.path.join(os.environ['HOME'],
                    '.local', 'share', 'rhythmbox', 'playlists.xml')

        if os.path.exists(rhythmbox_file):
            self.read(rhythmbox_file)

    def read(self, path):
        for pl in etree.parse(path).xpath('/rhythmdb-playlists/playlist'):
            if pl.get('type') != 'static':
                continue
            self.playlists.append(playlists.RhythmboxPlaylist(pl.get('name')))
            for song_location in pl.xpath('location'):
                clean_loc = urllib.parse.unquote(song_location.text)
                self.current_playlist.add_file(clean_loc)
