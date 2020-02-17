# -*- coding: UTF-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2020 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
from lxml import etree

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


def node2text(node):
    """Strip all text from a node and their children

    Parameters
    ----------
    node : etree._Element
        Element
    """
    stripchars = ("\n", "\t")

    nodetext = etree.tostring(node, method="text").decode()
    for c_ in stripchars:
        nodetext = nodetext.replace(c_, '')
    return nodetext
