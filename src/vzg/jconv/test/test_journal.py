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
import json
from lxml import etree
from pathlib import Path
from vzg.jconv.journal import JatsJournal
from vzg.jconv.converter.jats import JatsArticle
from vzg.jconv.gapi import JATS_SPRINGER_PUBTYPE, PUBTYPE_SOURCES
from vzg.jconv.utils.date import JatsDate

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = "plaintext"

logger = logging.getLogger(__name__)


class TestClassSpringer(unittest.TestCase):
    def setUp(self) -> None:
        self.fpath = Path("data/tests/springer/article.xml")
        self.jpath = Path("data/tests/springer/article_ppub.json")

        with open(self.jpath) as fh:
            self.testdata = json.load(fh)

        with open(self.fpath, "rb") as fh:
            self.dom = etree.parse(fh)
            self.article = JatsArticle(
                self.dom,
                JATS_SPRINGER_PUBTYPE.print,
                pubtype_source=PUBTYPE_SOURCES.basic,
            )

    def test01_journal_type(self):
        journal = JatsJournal(self.article)

        self.assertIsInstance(journal, JatsJournal, "type")

    def test02_journal_title(self):
        journal = JatsJournal(self.article)

        self.assertEqual(journal.title, self.testdata["journal"]["title"], "title")

    def test04_journal_date(self):
        journal = JatsJournal(self.article)

        self.assertIsInstance(journal.date, JatsDate, "date")

    def test05_journal_year(self):
        journal = JatsJournal(self.article)

        self.assertEqual(
            journal.date.year, int(self.testdata["journal"]["year"]), "year"
        )

    def test06_journal_ids(self):
        journal = JatsJournal(self.article)

        self.assertEqual(
            journal.ids,
            self.testdata["journal"]["journal_ids"],
            "ids",
        )

    def test07_journal_publisher(self):
        journal = JatsJournal(self.article)

        self.assertEqual(
            journal.publisher,
            self.testdata["journal"]["publisher"],
            "publisher",
        )


class TestClassDeGruyter(unittest.TestCase):
    def setUp(self) -> None:
        self.fpath = Path("data/tests/degruyter/article_abbrev.xml")
        self.jpath = Path("data/tests/degruyter/article_abbrev_ppub.json")

        with open(self.jpath) as fh:
            self.testdata = json.load(fh)

        with open(self.fpath, "rb") as fh:
            self.dom = etree.parse(fh)
            self.article = JatsArticle(
                self.dom,
                JATS_SPRINGER_PUBTYPE.print,
                pubtype_source=PUBTYPE_SOURCES.degruyter,
            )

    def test01_journal_type(self):
        journal = JatsJournal(self.article)

        self.assertIsInstance(journal, JatsJournal, "type")

    def test03_journal_abbrev_title(self):
        journal = JatsJournal(self.article)

        self.assertEqual(journal.title, self.testdata["journal"]["title"], "title")

    def test04_journal_date(self):
        journal = JatsJournal(self.article)

        self.assertIsInstance(journal.date, JatsDate, "date")

    def test05_journal_year(self):
        journal = JatsJournal(self.article)

        self.assertEqual(
            journal.date.year, int(self.testdata["journal"]["year"]), "year"
        )

    def test06_journal_ids(self):
        journal = JatsJournal(self.article)

        print(journal.ids)

        self.assertEqual(
            journal.ids,
            self.testdata["journal"]["journal_ids"],
            "ids",
        )

    def test07_journal_publisher(self):
        journal = JatsJournal(self.article)

        self.assertEqual(
            journal.publisher,
            self.testdata["journal"]["publisher"],
            "publisher",
        )
