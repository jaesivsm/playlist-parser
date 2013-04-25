#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

import urllib
import logging
import xml.parsers.expat

logger = logging.getLogger(__name__)


class XmlParser(object):

	def __init__(self, xml_file=None):
		self.previous_tags = []
		self.current_tag = None

		self.__parser = xml.parsers.expat.ParserCreate()

		self.__parser.StartElementHandler = self.__parsing_start_element
		self.__parser.EndElementHandler = self.__parsing_end_element
		self.__parser.CharacterDataHandler = self.__parsing_char_data
		self.__parser.XmlDeclHandler = self.__parsing_xml_declaration

		if xml_file:
			self.parse(xml_file)

	def parse(self, file_to_parse=None):
		logger.info('Parsing %s' % file_to_parse)
		if file_to_parse:
			with open(file_to_parse, 'r') as fd:
				self.__parser.Parse(urllib.unquote(fd.read()))

	def __parsing_start_element(self, tag, attrs):
		self.previous_tags.append(self.current_tag)
		self.current_tag = tag
		return self.parsing_start_element(tag, attrs)

	def parsing_start_element(self, tag, attrs):
		pass

	def __parsing_char_data(self, data):
		return self.parsing_char_data(data)

	def parsing_char_data(self, data):
		pass

	def __parsing_end_element(self, tag):
		self.current_tag = self.previous_tags.pop()
		return self.parsing_end_element(tag)

	def parsing_end_element(self, tag):
		pass

	def __parsing_xml_declaration(self, version, encoding, standalone):
		self.encoding = encoding
