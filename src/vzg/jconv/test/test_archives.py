# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

import unittest
import zipfile
from pathlib import Path
from zope.interface import providedBy
from vzg.jconv.archives.springer import ArchiveSpringer
from vzg.jconv.converter.jats import JatsConverter
from vzg.jconv.interfaces import IConverter


__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


class TestSpringer(unittest.TestCase):

    def setUp(self) -> None:
        self.archive = Path("data/tests/springer/test_archive.zip")

        self.fpath = "data/tests/springer/article.xml"
        self.article = Path(self.fpath)

        with zipfile.ZipFile(self.archive, "w") as zfh:
            zfh.write(self.article)

        return super().setUp()

    def tearDown(self) -> None:
        if self.archive.is_file():
            self.archive.unlink()

        return super().tearDown()

    def test_file(self):
        """"""
        def t1(evt):
            archive = ArchiveSpringer(Path("dsdssdsd"))
            archive.num_files

        self.assertRaises(FileNotFoundError, t1, "Datei existiert nicht")

    def test_num(self):
        """"""
        archive = ArchiveSpringer(self.archive)

        self.assertEqual(archive.num_files, 1, "Anzahl der Dateien")

    def test_converter(self):
        """"""
        archive = ArchiveSpringer(self.archive)

        for conv in archive.converters:
            self.assertIn(IConverter, providedBy(conv), "IConverter")
            self.assertIsInstance(conv, JatsConverter, "Konverter")
            self.assertEqual(conv.name, self.fpath, "Name")
