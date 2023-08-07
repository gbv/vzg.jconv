# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

import logging
import tempfile
import zipfile
from lxml import etree
from pathlib import Path
from typing import Generator
from zope.interface import implementer
from vzg.jconv.interfaces import IArchive
from vzg.jconv.converter.jats import JatsConverter


__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


@implementer(IArchive)
class ArchiveSpringer:

    def __init__(self, archivepath: Path, converter_kwargs: dict = {}) -> None:
        self.archivepath = archivepath
        self.converter_kwargs = converter_kwargs

    @property
    def converters(self) -> Generator[JatsConverter, None, None]:
        """Create the converters"""
        logger = logging.getLogger(__name__)

        with zipfile.ZipFile(self.archivepath, "r") as zfh:
            for i, zinfo in enumerate(zfh.infolist()):
                msg = f"Bearbteite {zinfo.filename} ({i})"
                logger.debug(msg)

                self.converter_kwargs["name"] = zinfo.filename

                with tempfile.NamedTemporaryFile("w+b") as tmpfh:
                    tmpfh.write(zfh.read(zinfo))
                    tmpfh.flush()

                    try:
                        jatspath = Path(tmpfh.name)
                        jconv = JatsConverter(
                            jatspath, **self.converter_kwargs)
                    except (etree.Error,
                            KeyError,
                            ValueError,
                            IndexError,
                            OSError,
                            TypeError):
                        msg = "Konvertierungsproblem in "
                        msg += f"{self.archivepath.as_posix()} -> {zinfo.filename}"
                        logger.error(msg, exc_info=True)

                        continue

                    yield jconv

    @property
    def num_files(self) -> int:
        """How many files are in the archive"""
        with zipfile.ZipFile(self.archivepath, "r") as zfh:
            num = len(zfh.namelist())

        return num
