# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

import datetime
import logging
import zipfile
from dataclasses import dataclass, field
from lxml import etree
from pathlib import Path
from typing import Generator
from zope.interface import implementer
from vzg.jconv.gapi import NAMESPACES, OAI_DC_RECORD_XPATHS
from vzg.jconv.gapi import OAI_DC_HEADER_XPATHS, OAI_ARTICLES_TYPES
from vzg.jconv.interfaces import IArchive
from vzg.jconv.converter.oai import OAIDCConverter

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


@dataclass
class Header:

    record: etree._Element
    identifier: str = ""
    datestamp: datetime.datetime = None
    setspec: list[str] = field(default_factory=list)
    deleted: bool = False

    def __post_init__(self):
        self.identifier = self.__get_val__("identifier")

        dst = self.__get_val__("datestamp")

        try:
            self.datestamp = datetime.datetime.fromisoformat(dst)
        except ValueError:
            if dst[-1] == "Z":
                dst = dst[0:-1]

            self.datestamp = datetime.datetime.fromisoformat(dst)

        self.setspec = self.__get_val__("setspec", False)
        self.deleted = self.__get_val__("deleted")

    def __get_val__(self, key: str, single_node=True) -> any:
        if key not in OAI_DC_HEADER_XPATHS:
            return None

        val = self.record.xpath(
            OAI_DC_HEADER_XPATHS[key], namespaces=NAMESPACES)

        if isinstance(val, list) and single_node:
            if len(val) > 0:
                return val[0]
            else:
                return ""

        return val


class Metadata:
    def __init__(self, element, map):
        self._element = element
        self._map = map

    def element(self):
        return self._element

    def getMap(self):
        return self._map

    def getField(self, name):
        if name not in self._map:
            return None

        rtype, xstm = self._map[name]

        return self._element.xpath(xstm, namespaces=NAMESPACES)

    __getitem__ = getField


@implementer(IArchive)
class ArchiveOAIDC:

    def __init__(self, archivepath: Path, converter_kwargs: dict = {}) -> None:
        self.archivepath = archivepath
        self.converter_kwargs = converter_kwargs

    @property
    def converters(self) -> Generator[OAIDCConverter, None, None]:
        """Create the converters"""
        logger = logging.getLogger(__name__)

        with zipfile.ZipFile(self.archivepath, "r") as zfh:
            for i, zinfo in enumerate(zfh.infolist()):
                msg = f"Bearbeite {zinfo.filename} ({i})"
                logger.debug(msg)

                try:
                    dom = etree.fromstring(zfh.read(zinfo))
                    header = Header(dom)
                    record = Metadata(dom, OAI_DC_RECORD_XPATHS)

                    if self.converter_kwargs.get('article_type') == OAI_ARTICLES_TYPES.openedition:
                        if 'article' not in record.getField('type'):
                            continue
                    oiaconv = OAIDCConverter(header,
                                             record,
                                             **self.converter_kwargs)
                except (etree.Error,
                        KeyError,
                        ValueError,
                        IndexError,
                        OSError,
                        TypeError):

                    _path = self.archivepath.as_posix() if isinstance(
                        self.archivepath, Path) else self.archivepath
                    msg = "Konvertierungsproblem in "
                    msg += f"{_path}-> {zinfo.filename}"
                    logger.error(msg, exc_info=True)

                    continue

                yield oiaconv

    @property
    def num_files(self) -> int:
        """How many files are in the archive"""
        with zipfile.ZipFile(self.archivepath, "r") as zfh:
            num = len(zfh.namelist())

        return num
