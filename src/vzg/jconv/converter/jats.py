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
from vzg.jconv.interfaces import IConverter
from vzg.jconv.gapi import NAMESPACES
from vzg.jconv.gapi import JSON_SCHEMA
from vzg.jconv.langcode import ISO_639
from lxml import etree
import logging
import json
from vzg.jconv.gapi import JATS_SPRINGER_PUBTYPE
import jsonschema

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'

JATS_XPATHS = {}
JATS_XPATHS["lang_code"] = "//article-meta/title-group/article-title/@xml:lang"
JATS_XPATHS["journal-title"] = "//journal-meta/journal-title-group/journal-title/text()"
JATS_XPATHS["pub-date"] = """//article-meta/pub-date[@date-type="{pubtype}"]"""
JATS_XPATHS["pub-date-year"] = JATS_XPATHS["pub-date"] + """/year/text()"""
JATS_XPATHS["primary_id"] = """//article-meta/article-id[@pub-id-type="publisher-id"]/text()"""
JATS_XPATHS["article-title"] = "//article-meta/title-group/article-title/text()"


@implementer(IArticle)
class JatsArticle:
    """Convert a JATS XML File to a JSON object

    Parameters
    ----------
    dom : etree._ElementTree
        ElementTree
    pubtype : string

    iso639 : vzg.jconv.langcode.ISO_639

    Returns
    -------
    None
    """

    def __init__(self, dom, pubtype, iso639=None):
        self.dom = dom
        self.iso639 = ISO_639() if isinstance(iso639, type(None)) else iso639
        self.pubtype = pubtype

    @property
    def lang_code(self):
        """Article lang_code"""
        logger = logging.getLogger(__name__)
        attributes = self.xpath(JATS_XPATHS['lang_code'])
        try:
            lang_code = self.iso639.i1toi2[attributes[0]]
        except IndexError:
            logger.error("no lang_code")
        except KeyError:
            logger.error("no lang_code")

        return [lang_code]

    @property
    def journal(self):
        """Article journal"""
        logger = logging.getLogger(__name__)

        pdict = {"title": "", "year": ""}

        expression = JATS_XPATHS["journal-title"]
        node = self.xpath(expression)
        try:
            pdict['title'] = node[0]
        except IndexError:
            logger.error("no journal title")

        expression = JATS_XPATHS["pub-date-year"].format(pubtype=self.pubtype)
        node = self.xpath(expression)

        try:
            pdict['year'] = node[0]
        except IndexError:
            logger.error("no journal year")

        return pdict

    @property
    def jdict(self):
        """"""
        jdict = {"lang_code": self.lang_code,
                 "journal": self.journal,
                 "primary_id": self.primary_id,
                 "title": self.title}

        return jdict

    @property
    def json(self):
        """"""
        return json.dumps(self.jdict)

    @property
    def primary_id(self):
        """Article primary_id"""
        logger = logging.getLogger(__name__)
        expression = JATS_XPATHS["primary_id"]
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

        expression = JATS_XPATHS["article-title"]
        node = self.xpath(expression)

        try:
            return node[0]
        except IndexError:
            logger.error("no title")

        return ''

    def xpath(self, expression):
        return self.dom.xpath(expression, namespaces=NAMESPACES)


@implementer(IConverter)
class JatsConverter:
    """Convert a JATS XML File to JSON Objects

    Parameters
    ----------
    jatspath : pathlib.Path
        Path object with the JATS XML file
    iso639 : vzg.jconv.langcode.ISO_639

    validate : bool
        Validate each IArticle
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

    >>> conv = JatsConverter(xpath)
    >>> conv.run()
    >>> conv.articles
    []
    """

    def __init__(self, jatspath, iso639=None, validate=False):
        self.jatspath = jatspath
        self.articles = []

        if not self.jatspath.is_file():
            raise OSError

        with open(self.jatspath, 'rb') as fh:
            self.dom = etree.parse(fh)

        self.iso639 = ISO_639() if isinstance(iso639, type(None)) else iso639

        self.validate = validate

    @property
    def pubtypes(self):
        """Try to guess the formats of publication.

        Depends on the publisher.

        Springer sets the date-type attribute to certain values
        """
        pubtypes = []

        for entry in JATS_SPRINGER_PUBTYPE:
            expression = JATS_XPATHS["pub-date"].format(pubtype=entry.value)
            nodes = self.dom.xpath(expression, namespaces=NAMESPACES)

            if len(nodes) > 0:
                pubtypes.append(entry)

        return pubtypes

    def run(self):
        """"""
        logger = logging.getLogger(__name__)

        for pubtype in self.pubtypes:
            article = JatsArticle(self.dom,
                                  pubtype.value,
                                  self.iso639)

            if self.validate:
                try:
                    jsonschema.validate(instance=article.jdict,
                                        schema=JSON_SCHEMA)
                    self.articles.append(article)
                except jsonschema.ValidationError as Exc:
                    logger.error(Exc, exc_info=False)

                continue

            self.articles.append(article)
