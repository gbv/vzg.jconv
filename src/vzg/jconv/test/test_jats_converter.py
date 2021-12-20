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
import sys
import unittest
import logging
from pathlib import Path
from vzg.jconv.converter.jats import JatsConverter
from vzg.jconv.converter.jats import JatsArticle
from lxml import etree
from pprint import pprint

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'

logger = logging.getLogger(__name__)
logger.level = logging.INFO
# stream_handler = logging.StreamHandler(sys.stdout)
# logger.addHandler(stream_handler)


class TestCase(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)

        self.fpath = Path("data/tests/springer/article.xml")
        self.fpaths = {"emerald": Path(
            "data/tests/emerald/article_emerald.xml")}

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test01(self):
        """Wrong path"""
        tpath = Path("sddsdsds.xml")

        with self.assertRaises(OSError):
            JatsConverter(tpath)

    def test02(self):
        """DOM"""
        with open(self.fpath, 'rb') as fh:
            dom = etree.parse(fh)

        self.assertIsInstance(dom, etree._ElementTree, "DOM")

    def test03(self):
        """run"""
        jconv = JatsConverter(self.fpath)

        self.assertTrue(len(jconv.articles) == 0, "articles")

        jconv.run()

        self.assertTrue(len(jconv.articles) == 2, "articles")

        for article in jconv.articles:
            self.assertIsInstance(article, JatsArticle, "article")

    def test04(self):
        """validate"""
        jconv = JatsConverter(self.fpath, validate=True)

        self.assertTrue(len(jconv.articles) == 0, "articles")

        jconv.run()

        self.assertTrue(len(jconv.articles) == 2, "articles")

        for article in jconv.articles:
            self.assertIsInstance(article, JatsArticle, "article")
            # pprint(article.json)

    def test05(self):
        """validate emerald"""
        jconv = JatsConverter(self.fpaths["emerald"], validate=True)

        self.assertTrue(len(jconv.articles) == 0, "articles")

        jconv.run()

        self.assertTrue(len(jconv.articles) == 1, "articles")

        for article in jconv.articles:
            self.assertIsInstance(article, JatsArticle, "article")
            # pprint(article.jdict)
            # print(article.json)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)
