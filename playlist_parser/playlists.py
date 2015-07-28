import os.path
import logging
from copy import deepcopy
from math import ceil, log10

from playlist_parser import utils
from playlist_parser.songs import Song
from playlist_parser.utils import to_fat_compat

logger = logging.getLogger(__name__)


class Playlist:

    def __init__(self, name=None, encoding='UTF8', **kwargs):
        logger.info('Creating playlist %r' % name)
        self.name = name
        self.songs = []
        self.encoding = encoding

    def add_song(self, song):
        if song is not None:
            self.songs.append(song)

    def add_file(self, path):
        self.songs.append(Song(path))

    def __iter__(self):
        return iter(self.songs)

    def __getitem__(self, key):
        return self.songs[key]

    def copy(self, dst):
        new_pl = Playlist(self.name, self.encoding)
        logger.info('Copying %r to %s' % (self, dst))
        track_nb_format = "%%0%dd - " % ceil(log10(len(self.songs) + 1))
        for i, song in enumerate(self):
            new_pl.add_song(song.copy(os.path.join(dst, self.name),
                                      track_nb_format % i))
        return new_pl

    def export(self, dst, old_root):
        new_pl = Playlist(self.name, self.encoding)
        logger.info('Exporting playlist %r => %r', self, dst)
        for song in self:
            song = deepcopy(song)
            # replacing old root with new root in the playlist file
            if old_root and song.location.startswith(old_root):
                folder_dst = os.path.dirname(song.location)[len(old_root):]
                folder_dst = os.path.join(dst, folder_dst.lstrip('/'))
                new_pl.add_song(song.copy(folder_dst))
            else:
                logger.warn("song %r couldn't be processed", song)
        return new_pl

    def __str__(self):
        return self.name.encode(self.encoding)

    def __repr__(self):
        return r'<Playlist %r (%d songs)>' % (self.name, len(self.songs))


class RhythmboxPlaylist(Playlist):

    def add_file(self, path):
        if path.startswith('file://'):
            self.add_song(Song(path[7:]))
        else:
            self.songs[-1].location += path
            self.songs[-1].set_title()


class FilePlaylist(Playlist):

    def __init__(self, path, read=True, old_root=None, new_root=None, **kw):
        super().__init__(os.path.splitext(os.path.basename(path))[0], **kw)

        self.path = path
        self.new_root, self.old_root = new_root, old_root
        self.directory = os.path.dirname(path)

        if read and os.path.exists(path):
            self.read(path)

    @classmethod
    def from_playlist(cls, playlist, old_root, new_root):
        new_pl = cls(playlist.name, read=False,
                     old_root=old_root, new_root=new_root)
        new_pl.songs = playlist.songs
        return new_pl

    def get_asb_path(self, path):
        if os.path.isabs(path):
            return path
        return os.path.join(self.directory, path)

    @property
    def songs_to_plfile(self):
        for song in self:
            if not song.location:
                continue
            song = deepcopy(song)
            # replacing old root with new root in the playlist file
            if self.old_root is not None and self.new_root is not None:
                if song.location.startswith(self.old_root):
                    song.location = os.path.join(self.new_root,
                               song.location[len(self.old_root):].lstrip('/'))
                else:
                    song.location = os.path.join(self.new_root,
                                                 song.location.lstrip('/'))
                song.location = to_fat_compat(song.location)
            yield song

    def write(self, path):
        raise NotImplementedError('should be overridden in child class')


class PlsPlaylist(FilePlaylist, utils.XmlParser):

    def __init__(self, playlist_path, read=True, **kwargs):
        utils.XmlParser.__init__(self, playlist_path)
        super(PlsPlaylist, self).__init__(playlist_path, read, **kwargs)
        self.current_song = None

    def parsing_start_element(self, tag, attrs):
        if tag == "track":
            self.current_song = Song(encoding=self.encoding)

    def parsing_char_data(self, data):
        if "track" in self.previous_tags and self.current_song is not None:
            if self.current_tag == "location":
                data = self.get_asb_path(data)
            setattr(self.current_song, self.current_tag, data)

    def parsing_end_element(self, tag):
        if tag == "track" and self.current_song is not None:
            self.add_song(self.current_song)
            self.current_song = None


class M3uPlaylist(FilePlaylist):

    def __init__(self, playlist_path, read=True, **kwargs):
        super().__init__(playlist_path, read, **kwargs)
        self.current_song = None

    def __parse_line(self, line, fd, path):
        if line.startswith('#EXTINF:'):
            line = line.strip()[8:]
            length = creator = title = location = None
            if ',' in line:
                length, line = line.split(',', 1)
            if ' - ' in line:
                creator, title = line.split(' - ', 1)
            else:
                title = line
            for line in fd:
                location = self.get_asb_path(line.strip())
                if os.path.exists(location):
                    break
                elif location.startswith('#EXT'):
                    self.__parse_line(line, fd, path)
                    return
                else:
                    logger.warn('File not found %r in playlist %r'
                            % (location, path))
                    location = None
            song = Song(location, title)
            if creator is not None:
                song.creator = creator
            self.add_song(song)
        elif line.startswith('#EXTM3U'):
            return
        else:
            if os.path.exists(line):
                self.add_file(line)
            else:
                logger.warn('File not found %r in playlist %r' % (line, path))

    def read(self, path):
        logger.info('Parsing %r' % path)
        with open(path, 'r') as fd:
            if fd.encoding:
                self.encoding = fd.encoding
            for line in fd:
                self.__parse_line(line, fd, path)

    def write(self, path):
        logger.info('Writing %r' % path)
        with open(path, 'w') as fd:
            fd.write('#EXTM3U\n')
            for song in self.songs_to_plfile:
                logger.debug('Adding song %r to playlist %r' % (song, self))
                fd.write('#EXTINF:%s,%s%s%s\n'
                         % (song.length if song.length else '',
                            song.creator if song.creator else '',
                            ' - ' if song.creator and song.title else '',
                            song.title if song.title else ''))
                fd.write("%s\n" % song.location)


# vim: set et sts=4 sw=4 tw=120:
