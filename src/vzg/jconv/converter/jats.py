# -*- coding: UTF-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2020 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
from zope.interface import implementer
from vzg.jconv.interfaces import IArticle
from vzg.jconv.gapi import NAMESPACES
from vzg.jconv.langcode import ISO_639
from lxml import etree
import logging
import json

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


@implementer(IArticle)
class Jats:
    """Convert a JATS XML File to JSON

    Parameters
    ----------
    jatspath : pathlib.Path
        Path object with the JATS XML file

    Returns
    -------
    None

    Raises
    ------
    OSError
        If it is not a file
    lxml.etree.XMLSyntaxError
        Invalid XML

    Examples
    --------
    These are written in doctest format, and should illustrate how to
    use the function.

    >>> a=[1,2,3]
    >>> print [x + 3 for x in a]
    [4, 5, 6]
    """

    def __init__(self, jatspath, iso639=None):
        self.jatspath = jatspath

        if not self.jatspath.is_file():
            raise OSError

        with open(self.jatspath, 'rb') as fh:
            self.dom = etree.parse(fh)

        self.iso639 = ISO_639() if isinstance(iso639, type(None)) else iso639

    @property
    def lang_code(self):
        """Article lang_code"""
        logger = logging.getLogger(__name__)
        attributes = self.xpath(
            "//article-meta/title-group/article-title/@xml:lang")
        try:
            lang_code = self.iso639.i1toi2[attributes[0]]
        except IndexError:
            logger.error("no lang_code")
        except KeyError:
            logger.error("no lang_code")

        return lang_code

    @property
    def journal(self):
        """Article journal"""
        logger = logging.getLogger(__name__)

        pdict = {"title": "", "year": ""}

        expression = """//journal-meta/journal-title-group/journal-title/text()"""
        node = self.xpath(expression)
        try:
            pdict['title'] = node[0]
        except IndexError:
            logger.error("no journal title")

        expression = """//article-meta/pub-date/year/text()"""
        node = self.xpath(expression)
        try:
            pdict['year'] = node[0]
        except IndexError:
            logger.error("no journal year")

        return pdict

    @property
    def json(self):
        """"""
        jdict = {"lang_code": self.lang_code,
                 "journal": self.journal,
                 "primary_id": self.primary_id,
                 "title": self.title}
        return json.dumps(jdict)

    @property
    def primary_id(self):
        """Article primary_id"""
        logger = logging.getLogger(__name__)
        expression = """//article-meta/article-id[@pub-id-type="publisher-id"]/text()"""
        node = self.xpath(expression)

        pdict = {"type": "SPRINGER", "id": ""}
        try:
            pdict['id'] = node[0]
        except IndexError:
            logger.error("no title")

        return pdict

    @property
    def title(self):
        """Article title"""
        logger = logging.getLogger(__name__)

        expression = "//article-meta/title-group/article-title/text()"
        node = self.xpath(expression)

        try:
            return node[0]
        except IndexError:
            logger.error("no title")

        return ''

    def xpath(self, expression):
        return self.dom.xpath(expression, namespaces=NAMESPACES)
