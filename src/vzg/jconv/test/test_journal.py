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

        with open(self.fpath, "rb") as fh:
            self.dom = etree.parse(fh)

    def test01_journal_type(self):
        journal = Journal(self.dom)

        self.assertIsInstance(journal, Journal, "type")

    def test02_journal_title(self):
        journal = Journal(self.dom)

        self.assertEqual(journal.title, "Zeitschrift für Konfliktmanagement", "title")
