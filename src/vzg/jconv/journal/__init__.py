# -*- coding: utf-8 -*-
"""Journal

##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
import logging
from zope.interface import implementer
from vzg.jconv.interfaces import IJournal
from vzg.jconv.gapi import NAMESPACES
from vzg.jconv.gapi import JATS_SPRINGER_PUBTYPE
from vzg.jconv.gapi import PUBTYPE_SOURCES
from vzg.jconv.gapi import JATS_SPRINGER_PUBTYPE, PUBTYPE_SOURCES
from vzg.jconv.gapi import JATS_SPRINGER_JOURNALTYPE
from vzg.jconv.utils.date import JatsDate
from vzg.jconv.utils import get_pubtype_suffix
from lxml import etree

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = "plaintext"

JATS_XPATHS = {}

JATS_XPATHS["journal-title"] = "//journal-meta/journal-title-group/journal-title/text()"
JATS_XPATHS[
    "abbrev-journal-title"
] = """//journal-meta/journal-title-group/abbrev-journal-title[@abbrev-type="full"]/text()"""
JATS_XPATHS["pub-date"] = """//article-meta/pub-date[@date-type="{pubtype}"]"""
JATS_XPATHS[
    "pub-date-pubtype-val"
] = """//article-meta/pub-date[@pub-type="{pubtype}"]"""
JATS_XPATHS[
    "pub-date-format"
] = """//article-meta/pub-date[@publication-format="{pubtype}"]"""
JATS_XPATHS["pub-date-year"] = JATS_XPATHS["pub-date"] + """/year/text()"""
JATS_XPATHS[
    "journal-id"
] = """//journal-meta/journal-id[@journal-id-type="{journaltype}"]/text()"""
JATS_XPATHS["journal-issn"] = """//journal-meta/issn[@pub-type="{pubtype}"]/text()"""
JATS_XPATHS[
    "journal-issn-pformat"
] = """//journal-meta/issn[@publication-format="{pubtype}"]/text()"""
JATS_XPATHS["publisher-name"] = """//journal-meta/publisher/publisher-name/text()"""
JATS_XPATHS["publisher-place"] = """//journal-meta/publisher/publisher-loc/text()"""
JATS_XPATHS["journal-volume"] = """//article-meta/volume/text()"""
JATS_XPATHS["journal-issue"] = """//article-meta/issue/text()"""
JATS_XPATHS["journal-start_page"] = """//article-meta/fpage/text()"""
JATS_XPATHS["journal-end_page"] = """//article-meta/lpage/text()"""


@implementer(IJournal)
class JatsJournal:
    def __init__(self, article: etree._ElementTree) -> None:
        self.article = article

        self.jids = {
            "emerald": [JATS_XPATHS["journal-id"].format(journaltype="publisher")],
            "basic": [JATS_XPATHS["journal-id"].format(journaltype="publisher-id")],
            "doi": [JATS_XPATHS["journal-id"].format(journaltype="doi")],
        }

        if self.article.pubtype_source == PUBTYPE_SOURCES.degruyter:
            self.jids[JATS_SPRINGER_PUBTYPE.electronic.value] = [
                JATS_XPATHS["journal-issn"].format(
                    pubtype=JATS_SPRINGER_PUBTYPE.electronic.value
                )
            ]
        else:
            self.jids[self.article.pubtype.value] = [
                JATS_XPATHS["journal-issn"].format(pubtype=self.article.pubtype.value),
                JATS_XPATHS["journal-issn-pformat"].format(
                    pubtype=self.article.pubtype.name
                ),
            ]

    def as_dict(self) -> dict:
        logger = logging.getLogger(__name__)
        journal = {"title": self.title, "year": "", "journal_ids": self.ids}
        jdate = self.date

        if isinstance(jdate.month, int):
            journal["month"] = f"{jdate.month:02}"
            if isinstance(jdate.day, int):
                journal["day"] = f"{jdate.day:02}"

        if isinstance(jdate.year, int):
            journal["year"] = f"{jdate.year}"

        if len(self.publisher) > 0:
            journal["publisher"] = self.publisher

        jdata = {
            "journal-volume": "volume",
            "journal-issue": "issue",
            "journal-start_page": "start_page",
            "journal-end_page": "end_page",
        }

        for xkey, attr in jdata.items():
            expression = JATS_XPATHS[xkey]
            node = self.xpath(expression)
            try:
                journal[attr] = node[0]
            except IndexError:
                logger.debug(f"no journal {attr}")

        return journal

    @property
    def date(self) -> JatsDate:
        """Look for the earliest date"""
        date_node = None

        for pubtype in JATS_SPRINGER_PUBTYPE:
            if self.article.pubtype_source == PUBTYPE_SOURCES.springer:
                expression = JATS_XPATHS["pub-date-format"].format(pubtype=pubtype.name)
            elif self.article.pubtype_source == PUBTYPE_SOURCES.degruyter:
                expression = JATS_XPATHS["pub-date-pubtype-val"].format(
                    pubtype=pubtype.value
                )
            else:
                expression = JATS_XPATHS["pub-date"].format(pubtype=pubtype.value)

            node = self.xpath(expression)

            if len(node) > 0:
                dnode = JatsDate(node[0])

                if isinstance(date_node, JatsDate):
                    if dnode.todate() < date_node.todate():
                        date_node = dnode
                else:
                    date_node = dnode

        return date_node

    @property
    def ids(self) -> list:
        logger = logging.getLogger(__name__)

        _ids = []

        for jtype, expressions in self.jids.items():
            for expression in expressions:
                node = self.xpath(expression)

                if len(node) == 0:
                    msg = f"no {jtype} journal_id ({self.article.pubtype.value})"
                    logger.debug(msg)
                    continue

                jid = {"type": jtype, "id": node[0]}

                if jtype == "basic":
                    jid["type"] = "springer"
                    if self.article.pubtype_source == PUBTYPE_SOURCES.degruyter:
                        jid["type"] = "degruyter"
                        jid["id"] += get_pubtype_suffix(self.article.pubtype.value)

                if jid["type"] in JATS_SPRINGER_JOURNALTYPE.__members__:
                    jid["type"] = JATS_SPRINGER_JOURNALTYPE[jid["type"]].value

                _ids.append(jid)

        return _ids

    @property
    def publisher(self) -> dict:
        logger = logging.getLogger(__name__)

        publisher = {}

        expression = JATS_XPATHS["publisher-name"]
        node = self.xpath(expression)
        try:
            publisher["name"] = node[0].strip()
        except IndexError:
            logger.debug("no publisher name")

        expression = JATS_XPATHS["publisher-place"]
        node = self.xpath(expression)
        try:
            publisher["place"] = node[0].strip()
        except IndexError:
            logger.debug("no publisher place")

        return publisher

    @property
    def title(self) -> str:
        """Journal title

        Returns:
            str: title
        """
        logger = logging.getLogger(__name__)

        title = ""

        for expression in (
            JATS_XPATHS["journal-title"],
            JATS_XPATHS["abbrev-journal-title"],
        ):
            node = self.xpath(expression)
            try:
                title = node[0].strip()
                break
            except IndexError:
                logger.debug(f"no journal title {expression}")

        return title

    def xpath(self, expression):
        return self.article.dom.xpath(expression, namespaces=NAMESPACES)
