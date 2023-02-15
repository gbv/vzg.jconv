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
from lxml import etree
from vzg.jconv.gapi import JATS_SPRINGER_AUTHORTYPE

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = "plaintext"


class Person:
    def __init__(self, node: etree._Element) -> None:
        self.node = node

    @property
    def __name_node__(self) -> etree._Element | None:
        """Name node (read-only)

        Returns:
            etree._Element: _description_
        """
        name_node = None

        if isinstance(self.node.find("name"), etree._Element):
            name_node = self.node.find("name")
        elif isinstance(self.node.find("name-alternatives"), etree._Element):
            name_node = self.node.xpath("name-alternatives/name")[0]

        return name_node

    @property
    def firstname(self) -> str | None:
        """Firstname (read-only)

        Returns:
            str: _description_
        """
        try:
            return self.__name_node__.xpath("given-names/text()")[0].strip()
        except AttributeError:
            pass

        return None

    @property
    def lastname(self) -> str | None:
        """Lastname (read-only)

        Returns:
            str: _description_
        """
        try:
            return self.__name_node__.xpath("surname/text()")[0].strip()
        except AttributeError:
            pass

        return None

    @property
    def fullname(self) -> str | None:
        """Fullname (read-only)

        Returns:
            str: _description_
        """
        if isinstance(self.firstname, str) and isinstance(self.lastname, str):
            return f"{self.firstname} {self.lastname}"
        return None

    @property
    def role(self) -> str | None:
        """Role

        Returns:
            str | None: _description_
        """
        logger = logging.getLogger(__name__)

        role = None

        try:
            role = JATS_SPRINGER_AUTHORTYPE[self.node.get("contrib-type")].value
        except KeyError:
            msg = "unknown authortype"
            logger.info(msg)

        return role

    def as_dict(self) -> dict:
        """Generate the person dict

        Returns:
            dict: _description_
        """
        logger = logging.getLogger(__name__)

        person = {
            "firstname": self.firstname,
            "lastname": self.lastname,
            "fullname": self.fullname,
        }

        logger.debug(person)

        for key, value in person.items():
            if len(value) == 0:
                msg = f"no {key}"
                logger.info(msg)
                return None

        if isinstance(self.role, str):
            person["role"] = self.role

        return person