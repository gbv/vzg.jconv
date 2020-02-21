# -*- coding: UTF-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2020 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
from zope.interface import implementer
from vzg.jconv.interfaces import IArticle
from vzg.jconv.interfaces import IConverter
from vzg.jconv.gapi import NAMESPACES
from vzg.jconv.gapi import JSON_SCHEMA
from vzg.jconv.gapi import JATS_SPRINGER_AUTHORTYPE
from vzg.jconv.gapi import JATS_SPRINGER_PUBTYPE
from vzg.jconv.gapi import JATS_SPRINGER_JOURNALTYPE
from vzg.jconv.langcode import ISO_639
from vzg.jconv.utils import node2text
from lxml import etree
import logging
import json
import jsonschema

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'

JATS_XPATHS = {}
JATS_XPATHS["lang_code"] = "//article-meta/title-group/article-title/@xml:lang"
JATS_XPATHS["journal-title"] = "//journal-meta/journal-title-group/journal-title/text()"
JATS_XPATHS["pub-date"] = """//article-meta/pub-date[@date-type="{pubtype}"]"""
JATS_XPATHS["pub-date-year"] = JATS_XPATHS["pub-date"] + """/year/text()"""
JATS_XPATHS["primary_id"] = """//article-meta/article-id[@pub-id-type="publisher-id"]/text()"""
JATS_XPATHS["other_ids_doi"] = """//article-meta/article-id[@pub-id-type="doi"]/text()"""
JATS_XPATHS["article-title"] = "//article-meta/title-group/article-title"
JATS_XPATHS["journal-id"] = """//journal-meta/journal-id[@journal-id-type="{journaltype}"]/text()"""
JATS_XPATHS["journal-issn"] = """//journal-meta/issn[@pub-type="{pubtype}"]/text()"""
JATS_XPATHS["journal-volume"] = """//article-meta/volume/text()"""
JATS_XPATHS["journal-issue"] = """//article-meta/issue/text()"""
JATS_XPATHS["journal-start_page"] = """//article-meta/fpage/text()"""
JATS_XPATHS["journal-end_page"] = """//article-meta/lpage/text()"""
JATS_XPATHS["publisher-name"] = """//journal-meta/publisher/publisher-name/text()"""
JATS_XPATHS["publisher-place"] = """//journal-meta/publisher/publisher-loc/text()"""
JATS_XPATHS["article-persons"] = """//article-meta/contrib-group/contrib"""
JATS_XPATHS["article-copyright"] = """//article-meta/permissions/copyright-statement/text()"""
JATS_XPATHS["article-license-type"] = """//article-meta/permissions/license/@license-type"""
JATS_XPATHS["article-oa-license"] = """//article-meta/permissions/license[contains(@xlink:href, 'creativecommons.org')]"""
JATS_XPATHS["affiliation"] = """//article-meta/contrib-group/aff[@id="{rid}"]"""
JATS_XPATHS["abstracts-lang_code"] = "//article-meta/abstract/@xml:lang"
JATS_XPATHS["abstracts"] = "//article-meta/abstract"
JATS_XPATHS["abstracts-sec"] = "//article-meta/abstract/sec"


@implementer(IArticle)
class JatsArticle:
    """Convert a JATS XML File to a JSON object

    Parameters
    ----------
    dom : etree._ElementTree
        ElementTree
    pubtype : string

    iso639 : vzg.jconv.langcode.ISO_639

    Returns
    -------
    None
    """

    def __init__(self, dom, pubtype, iso639=None):
        self.dom = dom
        self.iso639 = ISO_639() if isinstance(iso639, type(None)) else iso639
        self.pubtype = pubtype

    @property
    def abstracts(self):
        """Article abstracts"""

        logger = logging.getLogger(__name__)

        attributes = self.xpath(JATS_XPATHS["abstracts-lang_code"])

        abstracts = []
        abstract = {'text': ""}

        try:
            abstract["lang_code"] = self.iso639.i1toi2[attributes[0]]
        except IndexError:
            logger.error("no lang_code")
        except KeyError:
            logger.error("no lang_code")

        sections = self.xpath(JATS_XPATHS["abstracts-sec"])
        atext = []

        for secnode in sections:
            nodes = secnode.xpath("title")
            if len(nodes) > 0:
                atext.append(nodes[0].text)

            paras = [node2text(para) for para in secnode.xpath("p")]
            atext += paras

        atext = [para for para in atext if isinstance(para, str)]
        abstract["text"] += "\n\n".join(atext)

        if len(abstract.get("text", "")) >= 1:
            abstracts.append(abstract)

        return abstracts

    @property
    def copyright(self):
        """Article copyright"""
        logger = logging.getLogger(__name__)
        nodes = self.xpath(JATS_XPATHS['article-copyright'])

        copyr = ""

        try:
            copyr = nodes[0]
        except IndexError:
            logger.error("no copyright")

        return copyr

    @property
    def lang_code(self):
        """Article lang_code"""
        logger = logging.getLogger(__name__)
        attributes = self.xpath(JATS_XPATHS['lang_code'])
        try:
            lang_code = self.iso639.i1toi2[attributes[0]]
        except IndexError:
            logger.error("no lang_code")
        except KeyError:
            logger.error("no lang_code")

        return [lang_code]

    @property
    def journal(self):
        """Article journal"""
        logger = logging.getLogger(__name__)

        pdict = {"title": "",
                 "year": "",
                 "journal_ids": []}

        jids = {'springer': JATS_XPATHS["journal-id"].format(journaltype="publisher-id"),
                'doi': JATS_XPATHS["journal-id"].format(journaltype="doi"),
                self.pubtype: JATS_XPATHS["journal-issn"].format(pubtype=self.pubtype)}

        expression = JATS_XPATHS["journal-title"]
        node = self.xpath(expression)
        try:
            pdict['title'] = node[0]
        except IndexError:
            logger.error("no journal title")

        expression = JATS_XPATHS["pub-date"].format(pubtype=self.pubtype)
        node = self.xpath(expression)

        dfmt = {"day": "{0:02}", "month": "{0:02}", "year": "{0}"}
        for dentry in dfmt:
            try:
                xepr = f"{dentry}/text()"
                val = int(node[0].xpath(xepr)[0])
                pdict[dentry] = dfmt[dentry].format(val)
            except IndexError:
                msg = f"no journal {dentry}"
                logger.error(msg)

        for jtype, expression in jids.items():
            node = self.xpath(expression)

            if len(node) == 0:
                msg = f"no {jtype} journal_id ({self.pubtype})"
                logger.error(msg)
                continue

            jid = {'type': jtype, 'id': node[0]}

            if jid['type'] in JATS_SPRINGER_JOURNALTYPE.__members__:
                jid['type'] = JATS_SPRINGER_JOURNALTYPE[jid['type']].value

            pdict["journal_ids"].append(jid)

        publisher = {}

        expression = JATS_XPATHS["publisher-name"]
        node = self.xpath(expression)
        try:
            publisher['name'] = node[0]
        except IndexError:
            logger.error("no publisher name")

        expression = JATS_XPATHS["publisher-place"]
        node = self.xpath(expression)
        try:
            publisher['place'] = node[0]
        except IndexError:
            logger.error("no publisher place")

        if len(publisher) > 0:
            pdict["publisher"] = publisher

        jdata = {"journal-volume": "volume",
                 "journal-issue": "issue",
                 "journal-start_page": "start_page",
                 "journal-end_page": "end_page"}

        for xkey, attr in jdata.items():
            expression = JATS_XPATHS[xkey]
            node = self.xpath(expression)
            try:
                pdict[attr] = node[0]
            except IndexError:
                logger.error(f"no journal {attr}")

        return pdict

    @property
    def jdict(self):
        """"""
        jdict = {"abstracts": self.abstracts,
                 "copyright": self.copyright,
                 "lang_code": self.lang_code,
                 "journal": self.journal,
                 "persons": self.persons,
                 "primary_id": self.primary_id,
                 "other_ids": self.other_ids,
                 "title": self.title}

        if self.pubtype == JATS_SPRINGER_PUBTYPE.electronic.value:
            jdict['urls'] = self.urls

        return jdict

    @property
    def json(self):
        """"""
        return json.dumps(self.jdict)

    @property
    def other_ids(self):
        """Article other_ids"""
        logger = logging.getLogger(__name__)
        expression = JATS_XPATHS["other_ids_doi"]
        node = self.xpath(expression)

        pdict = {"type": "doi", "id": ""}
        try:
            pdict['id'] = node[0]
        except IndexError:
            logger.error(("no other_id (doi)", self.pubtype))

        return [pdict]

    @property
    def persons(self):
        """Article persons"""
        logger = logging.getLogger(__name__)

        persons = []

        expression = JATS_XPATHS["article-persons"]
        nodes = self.xpath(expression)

        for elem in nodes:
            person = {"fullname": ""}

            try:
                person["firstname"] = elem.xpath("name/given-names/text()")[0]
                person["fullname"] = person["firstname"]
            except IndexError:
                msg = "no firstname"
                logger.error(msg)

            try:
                person["lastname"] = elem.xpath("name/surname/text()")[0]
                person["fullname"] += f""" {person["lastname"]}"""
            except IndexError:
                msg = "no lastname"
                logger.error(msg)

            if len(person["fullname"]) == 0:
                msg = "no fullname"
                logger.error(msg)
                continue

            try:
                person['role'] = JATS_SPRINGER_AUTHORTYPE[elem.get(
                    "contrib-type")].value
            except KeyError:
                msg = "unknown authortype"
                logger.error(msg)
                continue

            try:
                affiliation = elem.xpath("""xref[@ref-type="aff"]""")[0]
            except IndexError:
                msg = "no affiliation"
                logger.error(msg)
                continue

            rid = affiliation.get("rid")

            if isinstance(rid, type(None)):
                msg = "no affiliation"
                logger.error(msg)
                continue

            aff_expression = JATS_XPATHS["affiliation"].format(rid=rid)

            try:
                affnode = self.xpath(aff_expression)[0]
            except IndexError:
                msg = "no affiliation"
                logger.error(msg)
                continue

            affdict = {}

            try:
                affdict['name'] = affnode.xpath(
                    """institution-wrap/institution[@content-type="org-name"]/text()""")[0]
            except IndexError:
                msg = "no affiliation name"
                logger.error(msg)

            affids = []

            for affid in affnode.xpath("""institution-wrap/institution-id"""):
                affiddict = {}

                affiddict['type'] = affid.get("institution-id-type")
                affiddict['id'] = affid.text

                affids.append(affiddict)

            affdict["affiliation_ids"] = affids

            person["affiliation"] = affdict

            persons.append(person)

        return persons

    @property
    def primary_id(self):
        """Article primary_id"""
        logger = logging.getLogger(__name__)
        expression = JATS_XPATHS["primary_id"]
        node = self.xpath(expression)

        pdict = {"type": "SPRINGER", "id": ""}
        try:
            pdict['id'] = node[0]
        except IndexError:
            logger.error("no primary_id")

        return pdict

    @property
    def title(self):
        """Article title"""
        logger = logging.getLogger(__name__)

        expression = JATS_XPATHS["article-title"]
        node = self.xpath(expression)

        try:
            return node2text(node[0])
        except IndexError:
            logger.error("no title")

        return ''

    @property
    def urls(self):
        """Article URLs"""
        logger = logging.getLogger(__name__)

        udict = {}

        expression = JATS_XPATHS["other_ids_doi"]

        try:
            doi = self.xpath(expression)[0]
        except IndexError:
            logger.error("no doi (url)")
            return []

        udict["url"] = f"https://dx.doi.org/{doi}"
        udict["scope"] = "34"
        udict["access_info"] = "unknown"

        expression = JATS_XPATHS["article-oa-license"]
        nodes = self.xpath(expression)

        if len(nodes) > 0:
            udict["access_info"] = "OALizenz"

        return [udict]

    def xpath(self, expression):
        return self.dom.xpath(expression, namespaces=NAMESPACES)


@implementer(IConverter)
class JatsConverter:
    """Convert a JATS XML File to JSON Objects

    Parameters
    ----------
    jatspath : pathlib.Path
        Path object with the JATS XML file
    iso639 : vzg.jconv.langcode.ISO_639

    validate : bool
        Validate each IArticle
    Returns
    -------
    None

    Raises
    ------
    OSError
        If it is not a file
    lxml.etree.XMLSyntaxError
        Invalid XML

    Examples
    --------

    >>> conv = JatsConverter(xpath)
    >>> conv.run()
    >>> conv.articles
    []
    """

    def __init__(self, jatspath, iso639=None, validate=False):
        self.jatspath = jatspath
        self.articles = []

        if not self.jatspath.is_file():
            raise OSError

        with open(self.jatspath, 'rb') as fh:
            self.dom = etree.parse(fh)

        self.iso639 = ISO_639() if isinstance(iso639, type(None)) else iso639

        self.validate = validate
        self.validation_failed = False

    @property
    def pubtypes(self):
        """Try to guess the formats of publication.

        Depends on the publisher.

        Springer sets the date-type attribute to certain values
        """
        pubtypes = []

        for entry in JATS_SPRINGER_PUBTYPE:
            expression = JATS_XPATHS["pub-date"].format(pubtype=entry.value)
            nodes = self.dom.xpath(expression, namespaces=NAMESPACES)

            if len(nodes) > 0:
                pubtypes.append(entry)

        return pubtypes

    def run(self):
        """"""
        logger = logging.getLogger(__name__)

        for pubtype in self.pubtypes:
            article = JatsArticle(self.dom,
                                  pubtype.value,
                                  self.iso639)

            if self.validate:
                try:
                    jsonschema.validate(instance=article.jdict,
                                        schema=JSON_SCHEMA)
                    self.articles.append(article)
                except jsonschema.ValidationError as Exc:
                    logger.error(Exc, exc_info=False)
                    self.validation_failed = True

                continue

            self.articles.append(article)
