#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

import logging

from playlist_parser import libraries

logger = logging.getLogger()

formatter = logging.Formatter('%(module)s - %(levelname)-8s %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

library = libraries.RhythmboxLibrary()
