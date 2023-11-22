# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

import datetime
import unittest
from pathlib import Path
from zope.interface import providedBy
from vzg.jconv.archives.oai import ArchiveOAIDC
from vzg.jconv.converter.oai import OAIArtcile_Openedition
from vzg.jconv.interfaces import IArticle
from vzg.jconv.gapi import OAI_ARTICLES_TYPES

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


class Openedition(unittest.TestCase):

    def setUp(self) -> None:
        self.baseurl = Path(
            "data/tests/oai/response.xml").absolute().as_posix()

        self.from_date = datetime.datetime(2023, 10, 9)
        self.until_date = datetime.datetime(2023, 10, 10)
        self.articles = []

        archive = ArchiveOAIDC(self.baseurl,
                               local_file=True,
                               from_date=self.from_date,
                               until_date=self.until_date,
                               converter_kwargs={"article_type": OAI_ARTICLES_TYPES.openedition,
                                                 "validate": False})

        for i, conv in enumerate(archive.converters):
            conv.run()
            self.articles += conv.articles

    def test_interface(self):
        """"""
        for article in self.articles:
            self.assertIn(IArticle, providedBy(article), "IArticle")
            self.assertIsInstance(
                article, OAIArtcile_Openedition, "Openedition Artikel")


class OpeneditionValidate(unittest.TestCase):

    def setUp(self) -> None:
        self.baseurl = Path(
            "data/tests/oai/response.xml").absolute().as_posix()

        self.from_date = datetime.datetime(2023, 10, 9)
        self.until_date = datetime.datetime(2023, 10, 10)
        self.articles = []

        archive = ArchiveOAIDC(self.baseurl,
                               local_file=True,
                               from_date=self.from_date,
                               until_date=self.until_date,
                               converter_kwargs={"article_type": OAI_ARTICLES_TYPES.openedition,
                                                 "validate": True})

        for i, conv in enumerate(archive.converters):
            conv.run()
            self.articles += conv.articles

    def test_interface(self):
        """"""
        from pprint import pprint
        for article in self.articles:
            self.assertIn(IArticle, providedBy(article), "IArticle")
            self.assertIsInstance(
                article, OAIArtcile_Openedition, "Openedition Artikel")
            # pprint(article.jdict)
