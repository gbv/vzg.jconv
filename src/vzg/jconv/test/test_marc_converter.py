# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2025 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

from dataclasses import dataclass
from pathlib import Path
from pymarc.record import Record
from vzg.jconv.archives.oai import MarcArchive
from vzg.jconv.converter.MarcXmlConverter import MarcConverter
from vzg.jconv.interfaces import IConverter
from zope.interface import providedBy
import pytest


@dataclass
class MarcXMLBase:
    archive: Path


@pytest.fixture
def setup_marcxml() -> MarcXMLBase:
    marcxml_base = MarcXMLBase(
        archive=Path("data/tests/ssoar/2025-09-02_12-30-47-001.zip"),
    )

    return marcxml_base


def test_converter(setup_marcxml: MarcXMLBase):
    archive = MarcArchive(setup_marcxml.archive)

    for i, conv in enumerate(archive.converters):
        assert isinstance(conv.record, Record)
        assert IConverter in providedBy(conv)
        assert isinstance(conv, MarcConverter)

        conv.run()
