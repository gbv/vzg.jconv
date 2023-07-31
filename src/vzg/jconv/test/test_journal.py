# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

import logging
import unittest
from lxml import etree
from pathlib import Path
from vzg.jconv.journal import Journal

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = "plaintext"

logger = logging.getLogger(__name__)


class TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.fpath = Path("data/tests/springer/article.xml")
        self.apath = Path("data/tests/degruyter/article_abbrev.xml")

        with open(self.fpath, "rb") as fh:
            self.dom_springer = etree.parse(fh)

        with open(self.apath, "rb") as fh:
            self.dom_degruyter = etree.parse(fh)

    def test01_journal_type(self):
        journal = Journal(self.dom_springer)

        self.assertIsInstance(journal, Journal, "type")

    def test02_journal_title(self):
        journal = Journal(self.dom_springer)

        self.assertEqual(journal.title, "Academic Psychiatry", "title")

    def test03_journal_abbrev_title(self):
        journal = Journal(self.dom_degruyter)

        self.assertEqual(journal.title, "Zeitschrift für Konfliktmanagement", "title")
