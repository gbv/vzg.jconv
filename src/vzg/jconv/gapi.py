# -*- coding: UTF-8 -*-
"""API
##############################################################################
#
# Copyright (c) 2020-2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
from enum import Enum, auto
from pathlib import Path
import json

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = "plaintext"


__schema_path__ = Path(__file__).parent.absolute() / "schema" / "article_schema.json"

NAMESPACES = {
    "xml": "http://www.w3.org/XML/1998/namespace",
    "xlink": "http://www.w3.org/1999/xlink",
    "mml": "http://www.w3.org/1998/Math/MathML",
}

with open(__schema_path__, "rt") as fh:
    JSON_SCHEMA = json.load(fh)


class JATS_SPRINGER_PUBTYPE(Enum):
    """"""

    electronic = "epub"
    print = "ppub"


class JATS_SPRINGER_JOURNALTYPE(Enum):
    """"""

    epub = "eissn"
    ppub = "pissn"


class JATS_SPRINGER_AUTHORTYPE(Enum):
    """"""

    author = "aut"


class JATS_PUBTYPE_SUFFIX(Enum):
    """"""

    electronic = "-e"
    print = "-p"


class PERSON_ID_TYPES(Enum):
    """"""

    orcid = "orcid"
    unknown = "unknown"


class PUBTYPE_SOURCES(Enum):
    basic = auto()
    degruyter = auto()
    springer = auto()


JATS_XPATHS = {}
JATS_XPATHS["lang_code"] = "//article-meta/title-group/article-title/@xml:lang"
JATS_XPATHS["primary_lang_code"] = "//article/@xml:lang"
JATS_XPATHS["journal-title"] = "//journal-meta/journal-title-group/journal-title/text()"
JATS_XPATHS[
    "abbrev-journal-title"
] = """//journal-meta/descendant::abbrev-journal-title[@abbrev-type="full"]/text()"""
JATS_XPATHS["pub-date"] = """//article-meta/pub-date[@date-type="{pubtype}"]"""
JATS_XPATHS["pub-date-pubtype"] = """//article-meta/pub-date[@pub-type]"""
JATS_XPATHS[
    "pub-date-pubtype-val"
] = """//article-meta/pub-date[@pub-type="{pubtype}"]"""
JATS_XPATHS[
    "pub-date-format"
] = """//article-meta/pub-date[@publication-format="{pubtype}"]"""
JATS_XPATHS["pub-date-year"] = JATS_XPATHS["pub-date"] + """/year/text()"""
JATS_XPATHS[
    "primary_id"
] = """//article-meta/article-id[@pub-id-type="publisher-id"]/text()"""
JATS_XPATHS[
    "other_ids_doi"
] = """//article-meta/article-id[@pub-id-type="doi"]/text()"""
JATS_XPATHS["article-title"] = "//article-meta/title-group/article-title"
JATS_XPATHS[
    "journal-id"
] = """//journal-meta/journal-id[@journal-id-type="{journaltype}"]/text()"""
JATS_XPATHS["journal-issn"] = """//journal-meta/issn[@pub-type="{pubtype}"]/text()"""
JATS_XPATHS[
    "journal-issn-pformat"
] = """//journal-meta/issn[@publication-format="{pubtype}"]/text()"""
JATS_XPATHS["journal-volume"] = """//article-meta/volume/text()"""
JATS_XPATHS["journal-issue"] = """//article-meta/issue/text()"""
JATS_XPATHS["journal-start_page"] = """//article-meta/fpage/text()"""
JATS_XPATHS["journal-end_page"] = """//article-meta/lpage/text()"""
JATS_XPATHS["publisher-name"] = """//journal-meta/publisher/publisher-name/text()"""
JATS_XPATHS["publisher-place"] = """//journal-meta/publisher/publisher-loc/text()"""
JATS_XPATHS["article-persons"] = """//article-meta/contrib-group/contrib"""
JATS_XPATHS[
    "article-copyright"
] = """//article-meta/permissions/copyright-statement/text()"""
JATS_XPATHS["article-copyright-short"] = """//article-meta/copyright-statement/text()"""
JATS_XPATHS[
    "article-license-type"
] = """//article-meta/permissions/license/@license-type"""
JATS_XPATHS[
    "article-custom-meta"
] = """//article-meta/custom-meta-group/custom-meta/meta-name"""
JATS_XPATHS[
    "article-oa-license"
] = """//article-meta/permissions/license[contains(@xlink:href, 'creativecommons.org')]"""
JATS_XPATHS["affiliation"] = """//article-meta/contrib-group/aff[@id="{rid}"]"""
JATS_XPATHS["abstracts-lang_code"] = "//article-meta/abstract/@xml:lang"
JATS_XPATHS["abstracts"] = "//article-meta/abstract"
JATS_XPATHS["abstracts-sec"] = "//article-meta/abstract/sec"
JATS_XPATHS["abstracts-sec-node"] = ".//sec"
JATS_XPATHS["subjects-lang_code"] = "//article-meta/kwd-group/@xml:lang"
JATS_XPATHS["subjects"] = "//article-meta/kwd-group"
