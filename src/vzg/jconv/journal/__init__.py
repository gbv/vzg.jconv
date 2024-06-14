# -*- coding: utf-8 -*-
"""Journal

##############################################################################
#
# Copyright (c) 2023-2024 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
import logging
import re
from zope.interface import implementer
from vzg.jconv.interfaces import IJournal
from vzg.jconv.gapi import NAMESPACES
from vzg.jconv.gapi import JATS_SPRINGER_PUBTYPE
from vzg.jconv.gapi import PUBTYPE_SOURCES
from vzg.jconv.gapi import JATS_SPRINGER_JOURNALTYPE
from vzg.jconv.gapi import JATS_XPATHS
from vzg.jconv.gapi import CAIRN_REGEX
from vzg.jconv.utils.date import JatsDate
from vzg.jconv.utils import get_pubtype_suffix
from lxml import etree

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = "plaintext"


@implementer(IJournal)
class JatsJournal:
    def __init__(self, article: etree._ElementTree) -> None:
        self.article = article

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
                expression = JATS_XPATHS["pub-date-format"].format(
                    pubtype=pubtype.name)
            elif self.article.pubtype_source == PUBTYPE_SOURCES.degruyter:
                expression = JATS_XPATHS["pub-date-pubtype-val"].format(
                    pubtype=pubtype.value
                )
            else:
                expression = JATS_XPATHS["pub-date"].format(
                    pubtype=pubtype.value)

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
    def jids(self) -> dict:
        jids = {
            "emerald": [JATS_XPATHS["journal-id"].format(journaltype="publisher")],
            "basic": [JATS_XPATHS["journal-id"].format(journaltype="publisher-id")],
            "doi": [JATS_XPATHS["journal-id"].format(journaltype="doi")],
            self.article.pubtype.value: [
                JATS_XPATHS["journal-issn"].format(
                    pubtype=self.article.pubtype.value),
                JATS_XPATHS["journal-issn-pformat"].format(
                    pubtype=self.article.pubtype.name
                ),
            ],
        }

        if self.article.pubtype_source == PUBTYPE_SOURCES.degruyter:
            if JATS_SPRINGER_PUBTYPE.electronic.value in jids:
                jids[JATS_SPRINGER_PUBTYPE.electronic.value].append(
                    JATS_XPATHS["journal-issn"].format(
                        pubtype=JATS_SPRINGER_PUBTYPE.electronic.value
                    )
                )
            else:
                jids[JATS_SPRINGER_PUBTYPE.electronic.value] = [
                    JATS_XPATHS["journal-issn"].format(
                        pubtype=JATS_SPRINGER_PUBTYPE.electronic.value
                    )
                ]

        return jids

    @property
    def ids(self) -> list:
        logger = logging.getLogger(__name__)

        _ids = []

        for jtype, expressions in self.jids.items():
            done = []

            for expression in expressions:
                if jtype in done:
                    continue

                node = self.xpath(expression)

                if len(node) == 0:
                    msg = f"no {jtype} journal_id ({expression})"
                    logger.debug(msg)
                    continue

                jid = {"type": jtype, "id": node[0]}

                if jtype == "basic":
                    jid["type"] = "springer"
                    if self.article.pubtype_source == PUBTYPE_SOURCES.degruyter:
                        jid["type"] = "degruyter"
                        jid["id"] += get_pubtype_suffix(
                            self.article.pubtype.value)

                if jid["type"] in JATS_SPRINGER_JOURNALTYPE.__members__:
                    jid["type"] = JATS_SPRINGER_JOURNALTYPE[jid["type"]].value

                _ids.append(jid)

                done.append(jtype)

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


@implementer(IJournal)
class CairnJournal:

    def __init__(self, record: any) -> None:
        self.record = record

        if len(self.record.getField('source')) < 1:
            raise TypeError("Unknown source")

        self.source = self.record.getField('source')[0]
        self.source_parts = [val.strip() for val in self.source.split("|")]

        self.source_type = len(self.source_parts)
        if self.source_type not in (4, 5, 6):
            msg = f"Unknown source: {self.source}"
            raise TypeError(msg)

        (self.issn, self.start_page, self.end_page,
         self.volume) = (None, None, None, None)
        (self.pdate_day, self.pdate_month, self.pdate_year) = (None, None, None)

        self.__parse_parts__()

    def __parse_parts__(self) -> None:
        parts = self.source_parts[2:]

        if match := re.match(CAIRN_REGEX["issn"], self.source_parts[-1]):
            self.issn = match.group("issn")
            parts = self.source_parts[2:-1]

        print(self.source_parts)
        for value in reversed(parts):
            print(value)
            match = re.match(CAIRN_REGEX["pages"], value)
            if self.start_page is None and match:
                self.start_page = match.group("start")
                self.end_page = match.group("end")

            match = re.match(CAIRN_REGEX["publish_date"], value)
            if self.pdate_day is None and match:
                self.pdate_day = match.group("day")
                self.pdate_month = match.group("month")
                self.pdate_year = match.group("year")

        if self.source_type == 6:
            self.volume = self.source_parts[2]

    def as_dict(self):
        """Dict representation"""
        jdict = {
            'day': self.pdate_day,
            'end_page': self.end_page,
            'issue': self.issue,
            "journal_ids": self.journal_ids,
            'month': self.pdate_month,
            'start_page': self.start_page,
            'title': self.jtitle,
            'year': self.jyear,
        }

        if self.volume is not None:
            jdict["volume"] = self.volume

        if self.issn is not None:
            jdict["journal_ids"] = self.journal_ids

        return jdict

    @property
    def issue(self) -> str:
        return self.source_parts[1]

    @property
    def journal_ids(self) -> list:
        if self.issn is not None:
            return [{"id": self.issn, "type": JATS_SPRINGER_JOURNALTYPE.epub.value}]
        return []

    @property
    def jtitle(self) -> str:
        return self.source_parts[0]

    @property
    def jyear(self) -> str:
        return self.pdate_year
