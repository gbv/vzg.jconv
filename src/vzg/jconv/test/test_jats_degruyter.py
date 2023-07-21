# -*- coding: UTF-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
import unittest
from vzg.jconv.converter.jats import JatsArticle
from vzg.jconv.gapi import JATS_SPRINGER_PUBTYPE, PUBTYPE_SOURCES
from pathlib import Path
import json
from lxml import etree

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = "plaintext"


class EPubArticle(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)

        self.fpath = Path("data/tests/degruyter/article.xml")
        self.jpath = Path("data/tests/degruyter/article_epub.json")

        with open(self.jpath) as fh:
            self.testdata = json.load(fh)

        with open(self.fpath, "rb") as fh:
            self.dom = etree.parse(fh)

        self.jobj = JatsArticle(
            self.dom,
            JATS_SPRINGER_PUBTYPE.electronic,
            pubtype_source=PUBTYPE_SOURCES.degruyter,
        )

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test01(self):
        """title"""
        self.assertEqual(self.jobj.title, self.testdata["title"], "title")

    def test02(self):
        """lang_code"""
        self.assertEqual(self.jobj.lang_code, self.testdata["lang_code"], "lang_code")

    def test03(self):
        """primary_id"""
        self.assertEqual(
            self.jobj.primary_id, self.testdata["primary_id"], "primary_id"
        )

    def test04(self):
        """journal"""
        self.assertEqual(self.jobj.journal, self.testdata["journal"], "journal")

    def test05(self):
        """other_ids"""
        self.assertEqual(self.jobj.other_ids, self.testdata["other_ids"], "other_ids")

    def test06(self):
        """persons"""
        self.assertEqual(self.jobj.persons, self.testdata["persons"], "persons")

    def test07(self):
        """copyright"""
        self.assertEqual(self.jobj.copyright, self.testdata["copyright"], "copyright")

    def test08(self):
        """abstracts"""
        self.assertEqual(self.jobj.abstracts, self.testdata["abstracts"], "abstracts")

    def test09(self):
        """urls"""
        self.assertEqual(self.jobj.urls, self.testdata["urls"], "urls")

    def test10(self):
        """subjects"""
        self.assertEqual(
            self.jobj.subjects, self.testdata["subject_terms"], "subject_terms"
        )

    def test11(self):
        """dateOfProduction"""
        self.assertNotIn("dateOfProduction", self.jobj.jdict, "dateOfProduction")


class PPubArticle(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)

        self.fpath = Path("data/tests/degruyter/article.xml")
        self.jpath = Path("data/tests/degruyter/article_ppub.json")

        with open(self.jpath) as fh:
            self.testdata = json.load(fh)

        with open(self.fpath, "rb") as fh:
            self.dom = etree.parse(fh)

        self.jobj = JatsArticle(
            self.dom,
            JATS_SPRINGER_PUBTYPE.print,
            pubtype_source=PUBTYPE_SOURCES.degruyter,
        )

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test01(self):
        """title"""
        self.assertEqual(self.jobj.title, self.testdata["title"], "title")

    def test02(self):
        """lang_code"""
        self.assertEqual(self.jobj.lang_code, self.testdata["lang_code"], "lang_code")

    def test03(self):
        """primary_id"""
        self.assertEqual(
            self.jobj.primary_id, self.testdata["primary_id"], "primary_id"
        )

    def test04(self):
        """journal"""
        self.assertEqual(self.jobj.journal, self.testdata["journal"], "journal")

    def test05(self):
        """other_ids"""
        self.assertEqual(self.jobj.other_ids, self.testdata["other_ids"], "other_ids")

    def test06(self):
        """persons"""
        self.assertEqual(self.jobj.persons, self.testdata["persons"], "persons")

    def test07(self):
        """copyright"""
        self.assertEqual(self.jobj.copyright, self.testdata["copyright"], "copyright")

    def test08(self):
        """abstracts"""
        self.assertEqual(self.jobj.abstracts, self.testdata["abstracts"], "abstracts")

    def test09(self):
        """urls"""
        self.assertNotIn("urls", self.testdata, "urls")

    def test10(self):
        """subjects"""
        self.assertEqual(
            self.jobj.subjects, self.testdata["subject_terms"], "subject_terms"
        )

    def test11(self):
        """dateOfProduction"""
        self.assertNotIn("dateOfProduction", self.jobj.jdict, "dateOfProduction")

    def test12(self):
        """eissn überprüfen"""
        itypes = [entry["type"] for entry in self.jobj.journal["journal_ids"]]
        self.assertIn("eissn", itypes, "eissn")
