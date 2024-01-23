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
from vzg.jconv.converter.oai import OAIDCConverter
from vzg.jconv.interfaces import IConverter

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


class TestOAIDC(unittest.TestCase):

    def setUp(self) -> None:
        self.baseurl = Path(
            "data/tests/oai/2024-01-23_10-59-52-001.zip").absolute().as_posix()

    def test_converter(self):
        """"""
        archive = ArchiveOAIDC(self.baseurl)

        for i, conv in enumerate(archive.converters):
            self.assertIn(IConverter, providedBy(conv), "IConverter")
            self.assertIsInstance(conv, OAIDCConverter, "Konverter")

            conv.run()
