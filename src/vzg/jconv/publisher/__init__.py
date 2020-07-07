# -*- coding: UTF-8 -*-
"""Pubisher Ids

https://opus.k10plus.de/frontdoor/deliver/index/docId/419/file/K10plus_Tabelle_2113.pdf

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
import re
import logging
from vzg.jconv.errors import NoPublisherError

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'

logger = logging.getLogger(__name__)
__cfld__ = Path(__file__).parent.absolute()
__cdatapath__ = __cfld__ / "publisher-codes.json"

with open(__cdatapath__) as fh:
    __jdata__ = json.load(fh)

PUBIDS = {}

for checkname, checkdata in __jdata__.items():
    logger.debug(checkname)

    if checkdata["operator"] == "regex":
        checkdata["compiled"] = re.compile(checkdata["pattern"])

    PUBIDS[checkname] = checkdata


def getPublisherId(publisher):
    """"""
    logger = logging.getLogger(__name__)

    for checkname, checkdata in PUBIDS.items():
        logger.debug(checkname)
        if checkdata["operator"] == "regex":
            if checkdata["compiled"].match(publisher):
                return checkdata["value"]

    raise NoPublisherError(publisher)
