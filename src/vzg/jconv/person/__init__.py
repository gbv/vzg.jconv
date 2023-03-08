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
from vzg.jconv.gapi import PERSON_ID_TYPES
from vzg.jconv.utils import flatten_line

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
        except (AttributeError, IndexError):
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
        except (AttributeError, IndexError):
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
            logger.debug(msg)

        return role

    @property
    def affiliation(self) -> dict | None:
        """_summary_

        Returns:
            dict | None: _description_
        """
        logger = logging.getLogger(__name__)

        stm_int_org_name = """institution[@content-type="org-name"]/text()"""
        stm_inst_name = """institution/text()"""

        try:
            affiliation = self.node.xpath("""xref[@ref-type="aff"]""")[0]
        except IndexError:
            msg = "no affiliation"
            logger.debug(msg)
            return None

        rid = affiliation.get("rid")

        if isinstance(rid, type(None)):
            msg = "no affiliation"
            logger.debug(msg)
            return None

        aff_expression = """//article-meta/contrib-group/aff[@id="{rid}"]""".format(
            rid=rid
        )

        try:
            affnode = self.node.xpath(aff_expression)[0]
        except IndexError:
            msg = "no affiliation"
            logger.debug(msg)
            return None

        if isinstance(affnode.find("institution-wrap"), etree._Element):
            affdict_ = {}
            inode = affnode.find("institution-wrap")
            affdict_["name"] = ""

            try:
                affdict_["name"] = flatten_line(inode.xpath(stm_int_org_name)[0])
            except IndexError:
                msg = "no affiliation name (org-name)"
                logger.debug(msg)

            try:
                affdict_["name"] = flatten_line(inode.xpath(stm_inst_name)[0])
            except IndexError:
                msg = "no affiliation name"
                logger.debug(msg)

            if len(affdict_["name"].strip()) == 0:
                return None

            affids = []

            for affid in inode.xpath("""institution-id"""):
                affiddict = {}

                affiddict["type"] = affid.get("institution-id-type")
                affiddict["id"] = affid.text

                affids.append(affiddict)

            affdict_["affiliation_ids"] = affids

            return affdict_

        return None

    @property
    def person_ids(self) -> list:
        """person_ids

        Returns:
            list | None: _description_
        """

        def create_id(node):
            iddict = {
                "type": node.attrib.get("contrib-id-type", "unknown"),
                "id": node.text,
            }

            try:
                iddict["type"] = PERSON_ID_TYPES[iddict["type"]].value
            except KeyError:
                iddict["type"] = PERSON_ID_TYPES.unknown.value

            return iddict

        return [create_id(node) for node in self.node.findall("contrib-id")]

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
            if value is None:
                msg = f"Missing {key} for person"
                logger.debug(msg)
                return None

        if isinstance(self.role, str):
            person["role"] = self.role

        if isinstance(self.affiliation, dict):
            person["affiliation"] = self.affiliation

        if len(self.person_ids) > 0:
            person["person_ids"] = self.person_ids

        return person
