# -*- coding: UTF-8 -*-
"""Interfaces
##############################################################################
#
# Copyright (c) 2020 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
from zope.interface import Attribute, Interface

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


class IArticle(Interface):
    """VZG Article"""

    journal = Attribute("Journal")
    json = Attribute("Article as JSON object")
    lang_code = Attribute("Language Code")
    primary_id = Attribute("Primäre ID des Datensatzes in der Datenquelle")
    title = Attribute("Article Title")


class IConverter(Interface):
    """Converter"""

    articles = Attribute("List of IArticle objects")

    def run(self):
        """Start the conversion"""
