#!/usr/bin/env python3
import os
import logging
from argparse import ArgumentParser

from playlist_parser import libraries, playlists


def set_logger(log_format='%(module)-9s - %(levelname)-8s - %(message)s'):
    logger = logging.getLogger()
    formatter = logging.Formatter(log_format)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(dest="action", action="store", help="a value among "
                        "'copy', 'exporttom3u', 'exporttopls', 'tom3u', "
                        "and 'topls'")
    parser.add_argument(dest="destination", action="store")
    parser.add_argument('-s', '--source', dest='source',
                        action='store', default=None)
    parser.add_argument('-r', '--rhythmbox', dest='rhythmbox',
                        action='store_true', default=False)
    parser.add_argument('--old-root', dest='old_root',
                        action='store', default=None)
    parser.add_argument('--new-root', dest='new_root',
                        action='store', default=None)
    args = parser.parse_args()
    args.destination = os.path.expanduser(args.destination)

    if not (args.source or args.rhythmbox):
        print("a source must be provided (-r or -s=<file>)")
        return False
    elif args.source and not os.path.isfile(args.source):
        print("%r is not an existing file" % args.source)
        return False
    return args


def main(args):
    song_set = None
    if args.rhythmbox:
        song_set = libraries.RhythmboxLibrary()
    else:
        song_set = libraries.Library()
        ext = os.path.splitext(args.source)[-1]
        if ext == '.m3u':
            song_set[0] = playlists.M3uPlaylist(args.source)
        elif ext == '.pls':
            song_set[0] = playlists.PlsPlaylist(args.source)
        else:
            print("unknown extention: %r" % ext)
            return False
    if not os.path.isdir(args.destination):
        os.makedirs(args.destination, exist_ok=True)
    if args.action == 'copy':
        song_set.copy(args.destination)
    elif args.action.startswith('export'):
        if not args.old_root:
            print("export funcs need old_root")
            return False
        song_set.export(args.destination, args.old_root)
    tom3u = args.action.endswith('tom3u')
    topls = args.action.endswith('topls')
    if tom3u or topls:
        pl_cls = playlists.M3uPlaylist if tom3u else playlists.PlsPlaylist
        for playlist in song_set:
            path = os.path.join(args.destination, "%s.%s" % (playlist.name,
                                                    "m3u" if tom3u else "pls"))
            new_pl = pl_cls(playlist.name, read=False,
                            old_root=args.old_root, new_root=args.new_root)
            new_pl.songs = playlist.songs
            new_pl.write(path)
    return True


if __name__ == "__main__":
    args = parse_args()
    set_logger()
    if not args:
        exit(2)
    result = main(args)
    exit(0 if result else 1)
