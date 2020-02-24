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
import re
from vzg.jconv.gapi import NAMESPACES

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'

# TeX formular
TEXREX = re.compile("(\${1,2}.*\${1,2})")
# Upper case greek letters within a formula
GREEX = re.compile(r"\\up(\w+)")


def node2text(node):
    """Strip all text from a node and their children

    Parameters
    ----------
    node : etree._Element
        Element
    """
    stripchars = ("\n", "\t")

    # remove mml:math
    expression = "inline-formula/alternatives/mml:math"
    for mathnode in node.xpath(expression, namespaces=NAMESPACES):
        mathnode.clear()

    # remove TeX commands
    # extract the formula description

    def greekup(matchobj):
        print(matchobj)
        gc_ = "\\"
        gc_ += matchobj.group(1)
        return gc_

    for texnode in node.iter("tex-math"):
        match = TEXREX.search(texnode.text)
        if match is not None:
            formula = match.group(1)
            formula = GREEX.sub(greekup, formula)
            newelem = etree.Element("tex-math")
            newelem.text = formula
            texnode.getparent().replace(texnode, newelem)

    nodebytes = etree.tostring(node, encoding="utf-8", method="text")
    nodetext = nodebytes.decode()

    for c_ in stripchars:
        nodetext = nodetext.replace(c_, '')

    return nodetext
