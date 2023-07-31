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
from lxml import etree

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = "plaintext"

JATS_XPATHS = {}

JATS_XPATHS["journal-title"] = "//journal-meta/journal-title-group/journal-title/text()"
JATS_XPATHS[
    "abbrev-journal-title"
] = """//journal-meta/journal-title-group/abbrev-journal-title[@abbrev-type="full"]/text()"""


@implementer(IJournal)
class Journal:
    def __init__(self, article: etree._ElementTree) -> None:
        self.article = article

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
        return self.article.xpath(expression, namespaces=NAMESPACES)
