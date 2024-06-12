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
import json
import unittest
from pathlib import Path
from zope.interface import providedBy
from vzg.jconv.archives.oai import ArchiveOAIDC
from vzg.jconv.converter.oai import OAIArticle_Openedition, OAIArticle_Cairn
from vzg.jconv.interfaces import IArticle
from vzg.jconv.gapi import OAI_ARTICLES_TYPES

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


class Cairn(unittest.TestCase):

    def setUp(self) -> None:
        self.baseurl = Path(
            "data/tests/oai/cairn.zip").absolute().as_posix()
        self.jpath = Path("data/tests/oai/article_cairn.json")

        with open(self.jpath) as fh:
            self.testdata = json.load(fh)

        self.header = None
        self.record = None

        archive = ArchiveOAIDC(self.baseurl,
                               converter_kwargs={"article_type": OAI_ARTICLES_TYPES.cairn,
                                                 "validate": True})

        for i, conv in enumerate(archive.converters):
            conv.run()

            self.header = conv.header
            self.record = conv.record

        self.article = OAIArticle_Cairn(self.header, self.record)

    def test_abstracts(self):
        """"""
        self.assertEqual(self.article.abstracts,
                         self.testdata["abstracts"], "abstracts")

    def test_dateOfProduction(self):
        """"""
        self.assertEqual(self.article.date_of_production,
                         self.testdata["dateOfProduction"], "dateOfProduction")

    def test_lang_code(self):
        """"""
        self.assertEqual(self.article.lang_code,
                         self.testdata["lang_code"], "lang_code")

    def test_interface(self):
        """"""
        self.assertIn(IArticle, providedBy(self.article), "IArticle")
        self.assertIsInstance(self.article,
                              OAIArticle_Cairn,
                              "Cairn Artikel")

    def test_journal(self):
        """"""
        self.assertEqual(self.article.journal,
                         self.testdata["journal"], "journal")

    def test_persons(self):
        """"""
        self.assertEqual(self.article.persons,
                         self.testdata["persons"], "persons")

    def test_primary_id(self):
        """"""
        self.assertEqual(self.article.primary_id,
                         self.testdata["primary_id"], "primary_id")

    def test_subject_terms(self):
        """"""
        self.assertEqual(self.article.subject_terms,
                         self.testdata["subject_terms"], "subject_terms")

    def test_title(self):
        """"""
        self.assertEqual(self.article.title, self.testdata["title"], "title")


class Openedition(unittest.TestCase):

    def setUp(self) -> None:
        self.baseurl = Path(
            "data/tests/oai/openedition.zip").absolute().as_posix()

        self.header = None
        self.record = None

        archive = ArchiveOAIDC(self.baseurl,
                               converter_kwargs={"article_type": OAI_ARTICLES_TYPES.openedition,
                                                 "validate": False})

        for i, conv in enumerate(archive.converters):
            conv.run()

            self.header = conv.header
            self.record = conv.record

        self.article = OAIArticle_Openedition(self.header, self.record)

    def test_interface(self):
        """"""
        self.assertIn(IArticle, providedBy(self.article), "IArticle")
        self.assertIsInstance(self.article,
                              OAIArticle_Openedition,
                              "Openedition Artikel")


class OpeneditionValidate(unittest.TestCase):

    def setUp(self) -> None:
        self.baseurl = Path(
            "data/tests/oai/openedition.zip").absolute().as_posix()
        self.jpath = Path("data/tests/oai/article_openedition.json")

        with open(self.jpath) as fh:
            self.testdata = json.load(fh)

        self.header = None
        self.record = None

        archive = ArchiveOAIDC(self.baseurl,
                               converter_kwargs={"article_type": OAI_ARTICLES_TYPES.openedition,
                                                 "validate": True})

        for i, conv in enumerate(archive.converters):
            self.header = conv.header
            self.record = conv.record

        self.article = OAIArticle_Openedition(self.header, self.record)

    def test_abstracts(self):
        """"""
        self.assertEqual(self.article.abstracts,
                         self.testdata["abstracts"], "abstracts")

    def test_dateOfProduction(self):
        """"""
        self.assertEqual(self.article.date_of_production,
                         self.testdata["dateOfProduction"], "dateOfProduction")

    def test_lang_code(self):
        """"""
        self.assertEqual(self.article.lang_code,
                         self.testdata["lang_code"], "lang_code")

    def test_interface(self):
        """"""
        self.assertIn(IArticle, providedBy(self.article), "IArticle")
        self.assertIsInstance(self.article,
                              OAIArticle_Openedition,
                              "Openedition Artikel")

    def test_journal(self):
        """"""
        self.assertEqual(self.article.journal["title"],
                         self.testdata["journal"]["title"], "journal")

        self.assertEqual(self.article.journal["year"],
                         self.testdata["journal"]["year"], "journal")

    def test_persons(self):
        """"""
        self.assertEqual(self.article.persons,
                         self.testdata["persons"], "persons")

    def test_primary_id(self):
        """"""
        self.assertEqual(self.article.primary_id,
                         self.testdata["primary_id"], "primary_id")

    def test_subject_terms(self):
        """"""
        self.assertEqual(self.article.subject_terms,
                         self.testdata["subject_terms"], "subject_terms")

    def test_title(self):
        """"""
        self.assertEqual(self.article.title, self.testdata["title"], "title")
