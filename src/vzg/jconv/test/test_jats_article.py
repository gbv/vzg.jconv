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
import unittest
import logging
from vzg.jconv.converter.jats import JatsArticle
from vzg.jconv.gapi import JATS_SPRINGER_PUBTYPE
from pathlib import Path
import json
from lxml import etree

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'

logger = logging.getLogger(__name__)
logger.level = logging.INFO
# stream_handler = logging.StreamHandler(sys.stdout)
# logger.addHandler(stream_handler)


class EPubArticle(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.fpath = Path("data/tests/springer/article.xml")
        self.jpath = Path("data/tests/springer/article_epub.json")

        with open(self.jpath) as fh:
            self.testdata = json.load(fh)

        with open(self.fpath, 'rb') as fh:
            self.dom = etree.parse(fh)

        self.jobj = JatsArticle(self.dom, JATS_SPRINGER_PUBTYPE.electronic)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test01(self):
        """title"""
        self.assertEqual(self.jobj.title, self.testdata['title'], "title")

    def test02(self):
        """lang_code"""
        self.assertEqual(self.jobj.lang_code,
                         self.testdata['lang_code'],
                         "lang_code")

    def test03(self):
        """primary_id"""
        self.assertEqual(self.jobj.primary_id,
                         self.testdata['primary_id'],
                         "primary_id")

    def test04(self):
        """journal"""
        self.assertEqual(self.jobj.journal,
                         self.testdata['journal'],
                         "journal")

    def test05(self):
        """other_ids"""
        self.assertEqual(self.jobj.other_ids,
                         self.testdata['other_ids'],
                         "other_ids")

    def test06(self):
        """persons"""
        self.assertEqual(self.jobj.persons,
                         self.testdata['persons'],
                         "persons")

    def test07(self):
        """copyright"""
        self.assertEqual(self.jobj.copyright,
                         self.testdata['copyright'],
                         "copyright")

    def test08(self):
        """abstracts"""
        self.assertEqual(self.jobj.abstracts,
                         self.testdata['abstracts'],
                         "abstracts")

    def test09(self):
        """urls"""
        self.assertEqual(self.jobj.urls,
                         self.testdata['urls'],
                         "urls")

    def test10(self):
        """subjects"""
        self.assertEqual(self.jobj.subjects,
                         self.testdata['subject_terms'],
                         "subject_terms")

    def test11(self):
        """dateOfProduction"""
        self.assertNotIn("dateOfProduction",
                         self.jobj.jdict,
                         "dateOfProduction")


class PPubArticle(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.fpath = Path("data/tests/springer/article.xml")
        self.jpath = Path("data/tests/springer/article_ppub.json")

        with open(self.jpath) as fh:
            self.testdata = json.load(fh)

        with open(self.fpath, 'rb') as fh:
            self.dom = etree.parse(fh)

        self.jobj = JatsArticle(self.dom, JATS_SPRINGER_PUBTYPE.print)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test01(self):
        """title"""
        self.assertEqual(self.jobj.title, self.testdata['title'], "title")

    def test02(self):
        """lang_code"""
        self.assertEqual(self.jobj.lang_code,
                         self.testdata['lang_code'],
                         "lang_code")

    def test03(self):
        """primary_id"""
        self.assertEqual(self.jobj.primary_id,
                         self.testdata['primary_id'],
                         "primary_id")

    def test04(self):
        """journal"""
        self.assertEqual(self.jobj.journal,
                         self.testdata['journal'],
                         "journal")

    def test05(self):
        """other_ids"""
        self.assertEqual(self.jobj.other_ids,
                         self.testdata['other_ids'],
                         "other_ids")

    def test06(self):
        """persons"""
        self.assertEqual(self.jobj.persons,
                         self.testdata['persons'],
                         "persons")

    def test07(self):
        """copyright"""
        self.assertEqual(self.jobj.copyright,
                         self.testdata['copyright'],
                         "copyright")

    def test08(self):
        """abstracts"""
        self.assertEqual(self.jobj.abstracts,
                         self.testdata['abstracts'],
                         "abstracts")

    def test09(self):
        """urls"""
        self.assertNotIn('urls', self.testdata, "urls")

    def test10(self):
        """subjects"""
        self.assertEqual(self.jobj.subjects,
                         self.testdata['subject_terms'],
                         "subject_terms")

    def test11(self):
        """dateOfProduction"""
        self.assertEqual(str(self.jobj.dateOfProduction),
                         self.testdata['dateOfProduction'],
                         "dateOfProduction")


class EPubArticlePublisher(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.fpath = Path("data/tests/springer/article.xml")
        self.jpath = Path("data/tests/springer/article_epub_publisher.json")

        with open(self.jpath) as fh:
            self.testdata = json.load(fh)

        with open(self.fpath, 'rb') as fh:
            self.dom = etree.parse(fh)

        self.jobj = JatsArticle(self.dom,
                                JATS_SPRINGER_PUBTYPE.electronic,
                                publisher="Emerald")

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test01(self):
        """title"""
        self.assertEqual(self.jobj.title, self.testdata['title'], "title")

    def test02(self):
        """lang_code"""
        self.assertEqual(self.jobj.lang_code,
                         self.testdata['lang_code'],
                         "lang_code")

    def test03(self):
        """primary_id"""
        self.assertEqual(self.jobj.primary_id,
                         self.testdata['primary_id'],
                         "primary_id")


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EPubArticle))
    unittest.TextTestRunner(verbosity=2).run(suite)
