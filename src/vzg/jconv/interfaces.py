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

    journal = Attribute("Zeitschrift")
    lang_code = Attribute("Sprachcode")
    primary_id = Attribute("Primäre ID des Datensatzes in der Datenquelle")
    title = Attribute("Titel der Zeitschrift")
