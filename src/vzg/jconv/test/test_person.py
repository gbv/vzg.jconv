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
from pathlib import Path
import json
from lxml import etree

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = "plaintext"

logger = logging.getLogger(__name__)


class TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.fpath = Path("data/tests/springer/article.xml")
        self.jpath = Path("data/tests/springer/article_ppub.json")

        with open(self.jpath) as fh:
            self.testdata = json.load(fh)

        with open(self.fpath, "rb") as fh:
            self.dom = etree.parse(fh)

        self.person_nodes = self.dom.xpath("""//article-meta/contrib-group/contrib""")
        self.person_data = self.testdata["persons"]

    def test_01(self):
        """Person node_name"""
        for node in self.person_nodes:
            person = Person(node)
            logger.debug(person.as_dict())
            assert isinstance(person.__name_node__, etree._Element)

    def test_02(self):
        """Check person data"""
        for i, node in enumerate(self.person_nodes):
            person = Person(node)
            assert person.as_dict() == self.person_data[i]
