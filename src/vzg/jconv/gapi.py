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
from enum import Enum
from pathlib import Path
import json
__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


__schema_path__ = Path(__file__).parent.absolute() / \
    "schema" / "article_schema.json"

NAMESPACES = {'xml': 'http://www.w3.org/XML/1998/namespace'}

with open(__schema_path__, "rt") as fh:
    JSON_SCHEMA = json.load(fh)


class JATS_SPRINGER_PUBTYPE(Enum):
    """"""

    electronic = "epub"
    print = "ppub"
