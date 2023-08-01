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
import io
import unittest
from lxml import etree
from vzg.jconv.utils.date import JatsDate

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = "plaintext"

XML_DATE_NUMBER = b"""
<date>
    <day>26</day>
    <month>05</month>
    <year>2018</year>
</date>
"""

XML_DATE_YEAR = b"""
<date>
    <year>2023</year>
</date>
"""

XML_DATE_NAME = b"""
<date>
    <month>May</month>
    <year>2023</year>
</date>
"""


class TestNumber(unittest.TestCase):
    def setUp(self) -> None:
        xfh = io.BytesIO()
        xfh.write(XML_DATE_NUMBER)
        xfh.seek(0)

        self.dom = etree.parse(xfh)

        self.jdate = JatsDate(self.dom)

        return super().setUp()

    def test_day(self):
        assert self.jdate.day == 26

    def test_date(self):
        dobj = datetime.date(2018, 5, 26)

        assert self.jdate.todate() == dobj

    def test_month(self):
        assert self.jdate.month == 5

    def test_year(self):
        assert self.jdate.year == 2018


class TestYear(unittest.TestCase):
    def setUp(self) -> None:
        xfh = io.BytesIO()
        xfh.write(XML_DATE_YEAR)
        xfh.seek(0)

        self.dom = etree.parse(xfh)

        self.jdate = JatsDate(self.dom)

        return super().setUp()

    def test_day(self):
        assert self.jdate.day is None

    def test_date(self):
        dobj = datetime.date(2023, 1, 1)

        assert self.jdate.todate() == dobj

    def test_month(self):
        assert self.jdate.month is None

    def test_year(self):
        assert self.jdate.year == 2023


class TestName(unittest.TestCase):
    def setUp(self) -> None:
        xfh = io.BytesIO()
        xfh.write(XML_DATE_NAME)
        xfh.seek(0)

        self.dom = etree.parse(xfh)

        self.jdate = JatsDate(self.dom)

        return super().setUp()

    def test_day(self):
        assert self.jdate.day is None

    def test_date(self):
        dobj = datetime.date(2023, 5, 1)

        assert self.jdate.todate() == dobj

    def test_month(self):
        assert self.jdate.month == 5

    def test_year(self):
        assert self.jdate.year == 2023
