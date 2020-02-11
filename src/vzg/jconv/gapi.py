# -*- coding: UTF-8 -*-
"""API
##############################################################################
#
# Copyright (c) 2020 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
from enum import Enum, auto

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


NAMESPACES = {'xml': 'http://www.w3.org/XML/1998/namespace'}


class JATS_PUBTYPE(Enum):
    """"""

    epub = auto()
    ppub = auto()
