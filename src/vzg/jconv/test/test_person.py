# -*- coding: UTF-8 -*-
"""Tests for Person Class

##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
import unittest
import logging
from vzg.jconv.person import Person
from vzg.jconv.gapi import JATS_SPRINGER_AUTHORTYPE
from pathlib import Path
import json
from lxml import etree

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = "plaintext"

logger = logging.getLogger(__name__)


class TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.fpath = Path("data/tests/springer/article.xml")
        self.ppath = Path("data/tests/springer/person.xml")
        self.jpath = Path("data/tests/springer/article_ppub.json")

        self.stm_person = """//article-meta/contrib-group/contrib"""

        with open(self.jpath) as fh:
            self.testdata = json.load(fh)

        with open(self.fpath, "rb") as fh:
            self.dom = etree.parse(fh)

        with open(self.ppath, "rb") as fh:
            self.dom_person = etree.parse(fh)

        self.person_data = self.testdata["persons"]

    def test_01(self):
        """Person node_name"""
        for node in self.dom.xpath(self.stm_person):
            person = Person(node)
            logger.debug(person.as_dict())
            assert isinstance(person.__name_node__, etree._Element)

    def test_02(self):
        """Check person data"""
        for i, node in enumerate(self.dom.xpath(self.stm_person)):
            person = Person(node)
            assert person.as_dict() == self.person_data[i]

    def test_03(self):
        """Check invalid data"""

        for i, node in enumerate(self.dom_person.xpath(self.stm_person)):
            person = Person(node)

            match i:
                case 0:
                    assert person.firstname is None
                    assert person.fullname is None
                    assert person.role is None
                    assert person.as_dict() is None
                case 1:
                    assert person.lastname is None
                    assert person.fullname is None
                    assert person.role == JATS_SPRINGER_AUTHORTYPE.author.value
                    assert person.as_dict() is None
                case 2:
                    assert person.affiliation is None
                    assert person.person_ids == []
                    assert isinstance(person.as_dict(), dict)
                    assert person.as_dict() != self.person_data[i]
                case 3:
                    assert isinstance(person.person_ids, list)
                    assert person.person_ids == self.person_data[i]["person_ids"]
