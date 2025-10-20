# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2025 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

import json
import pytest
from dataclasses import dataclass
from pathlib import Path
from vzg.jconv.archives.oai import MarcArchive
from vzg.jconv.interfaces import IArticle
from vzg.jconv.converter.MarcXmlConverter import MarcArticle
from zope.interface import providedBy


@dataclass
class MarcXMLBase:
    archive: Path
    article_xml: Path
    article_json: Path
    article: MarcArticle | None = None
    testdata: dict | None = None


@pytest.fixture
def setup_marcxml() -> MarcXMLBase:
    marcxml_base = MarcXMLBase(
        archive=Path("data/tests/ssoar/2025-09-02_12-30-47-001.zip"),
        article_xml=Path("data/tests/ssoar/oai_gesis_izsoz_de_document_104623.xml"),
        article_json=Path("data/tests/ssoar/oai_gesis_izsoz_de_document_104623.json"),
        article=MarcArticle,
    )

    with marcxml_base.article_json.open() as jfh:
        marcxml_base.testdata = json.load(jfh)

    archive = MarcArchive(marcxml_base.archive, validate=True)

    for i, conv in enumerate(archive.converters):
        conv.run()

        record = conv.record

    marcxml_base.article = MarcArticle(record)

    return marcxml_base


def test_abstracts(setup_marcxml: MarcXMLBase):
    assert setup_marcxml.article.abstracts == setup_marcxml.testdata["abstracts"]


def test_dateOfProduction(setup_marcxml: MarcXMLBase):
    assert (
        setup_marcxml.article.date_of_production
        == setup_marcxml.testdata["dateOfProduction"]
    )


def test_lang_code(setup_marcxml: MarcXMLBase):
    assert setup_marcxml.article.lang_code == setup_marcxml.testdata["lang_code"]


def test_interface(setup_marcxml: MarcXMLBase):
    assert IArticle in providedBy(setup_marcxml.article)
    assert isinstance(setup_marcxml.article, MarcArticle)


def test_journal(setup_marcxml: MarcXMLBase):
    assert setup_marcxml.article.journal == setup_marcxml.testdata["journal"]


def test_persons(setup_marcxml: MarcXMLBase):
    assert setup_marcxml.article.persons == setup_marcxml.testdata["persons"]


def test_primary_id(setup_marcxml: MarcXMLBase):
    assert setup_marcxml.article.primary_id == setup_marcxml.testdata["primary_id"]


def test_urls(setup_marcxml: MarcXMLBase):
    assert setup_marcxml.article.urls == setup_marcxml.testdata["urls"]


# def test_subject_terms(setup_marcxml: MarcXMLBase):
#     assert (
#         setup_marcxml.article.subject_terms == setup_marcxml.testdata["subject_terms"]
#     )


def test_title(setup_marcxml: MarcXMLBase):
    assert setup_marcxml.article.title == setup_marcxml.testdata["title"]
