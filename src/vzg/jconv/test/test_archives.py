# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2023-2025 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

import pytest
import unittest
import zipfile
from dataclasses import dataclass
from pathlib import Path
from zope.interface import providedBy
from vzg.jconv.archives.oai import ArchiveOAIDC
from vzg.jconv.archives.oai import MarcArchive
from vzg.jconv.archives.springer import ArchiveSpringer
from vzg.jconv.converter.jats import JatsConverter
from vzg.jconv.converter.MarcXmlConverter import MarcConverter
from vzg.jconv.converter.oai import OAIDCConverter
from vzg.jconv.interfaces import IConverter


@dataclass
class MarcXMLBase:
    archive: Path


@pytest.fixture
def setup_marcxml() -> MarcXMLBase:
    """"""
    marcxml_base = MarcXMLBase(
        archive=Path("data/tests/ssoar/2025-09-02_12-30-47-001.zip")
    )

    return marcxml_base


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


class TestOAIDC(unittest.TestCase):
    def setUp(self) -> None:
        self.baseurl = (
            Path("data/tests/oai/2024-01-23_10-59-52-001.zip").absolute().as_posix()
        )

    def test_num(self):
        """"""
        archive = ArchiveOAIDC(self.baseurl)

        self.assertEqual(archive.num_files, 19, "Anzahl der Dateien")

    def test_converter(self):
        """"""
        archive = ArchiveOAIDC(self.baseurl)

        for i, conv in enumerate(archive.converters):
            self.assertIn(IConverter, providedBy(conv), "IConverter")
            self.assertIsInstance(conv, OAIDCConverter, "Konverter")


def test_marcxml_num(setup_marcxml: MarcXMLBase):
    assert isinstance(setup_marcxml, MarcXMLBase)

    archive = MarcArchive(setup_marcxml.archive)
    assert archive.num_files == 7
