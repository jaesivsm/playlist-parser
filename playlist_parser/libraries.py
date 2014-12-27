import os
import logging

from playlist_parser import playlists, utils

logger = logging.getLogger(__name__)


class Library(object):

    def __init__(self):
        logging.info('Creating Library')
        self.playlists = []

    def __iter__(self):
        return iter(self.playlists)

    def __getitem__(self, key):
        return self.playlists[key]

    def copy(self, dst):
        logger.info('Copying %r to %s' % (self, dst))
        for playlist in self:
            playlist.copy(dst)


class RhythmboxLibrary(Library, utils.XmlParser):

    def __init__(self, rhythmbox_file=None):
        self.current_playlist = None
        if not rhythmbox_file:
            rhythmbox_file = os.path.join(os.environ['HOME'],
                    '.local', 'share', 'rhythmbox', 'playlists.xml')
        super(RhythmboxLibrary, self).__init__()
        utils.XmlParser.__init__(self, rhythmbox_file)

        if os.path.exists(rhythmbox_file):
            self.read(rhythmbox_file)

    def parsing_start_element(self, tag, attrs):
        if self.current_tag == "playlist":
            if attrs['type'] == "static":
                self.current_playlist = playlists.RhythmboxPlaylist(
                        attrs['name'], encoding=self.encoding)
            elif attrs['type'] == 'queue':
                self.current_playlist = 'queue'

    def parsing_char_data(self, data):
        if self.current_tag == "location":
            if self.current_playlist == 'queue':
                logger.debug('Ignoring queue file %r', data)
                return
            elif self.current_playlist == None:
                logger.error('[ERROR] No playlist to put %r', data)
                return
            self.current_playlist.add_file(data)

    def parsing_end_element(self, tag):
        if tag == "playlist" and self.current_playlist not in ('queue', None):
            self.playlists.append(self.current_playlist)
            logger.info(repr(self.current_playlist))
            self.current_playlist = None

# vim: set et sts=4 sw=4 tw=120:
