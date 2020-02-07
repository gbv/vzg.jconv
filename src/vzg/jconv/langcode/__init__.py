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
import json
from pathlib import Path

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


class ISO_639:
    """ISO-639 Codes

    Map ISO-639 Codes

    Examples
    --------
    These are written in doctest format, and should illustrate how to
    use the class.

    >>> iso = ISO_639()
    >>> iso.i1toi2['de']
    'ger'
    >>> iso.i2toi1['ger']
    'de'
    """

    def __init__(self):
        """"Initalize ISO data"""
        cfld = Path(__file__).parent.absolute()
        self.cdatapath = cfld / "language-codes.json"

        with open(self.cdatapath) as fh:
            self.jdata = json.load(fh)

        self.i1toi2 = {lentry["alpha2"]: lentry["alpha3-b"]
                       for lentry in self.jdata}

        self.i2toi1 = {lentry["alpha3-b"]: lentry["alpha2"]
                       for lentry in self.jdata}
