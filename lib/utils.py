import re
import logging
import xml.parsers.expat
from urllib.parse import unquote

logger = logging.getLogger(__name__)


def to_fat_compat(string):
    return string #re.sub('[:\*\?"<>\|]', '', string)
