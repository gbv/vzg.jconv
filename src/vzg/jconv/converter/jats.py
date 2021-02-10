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
from vzg.jconv.publisher import getPublisherId
from vzg.jconv.errors import NoPublisherError
from vzg.jconv.utils import node2text
from vzg.jconv.utils.date import JatsDate
from lxml import etree
import logging
import json
import jsonschema

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'

JATS_XPATHS = {}
JATS_XPATHS["lang_code"] = "//article-meta/title-group/article-title/@xml:lang"
JATS_XPATHS[
    "journal-title"] = "//journal-meta/journal-title-group/journal-title/text()"
JATS_XPATHS["pub-date"] = """//article-meta/pub-date[@date-type="{pubtype}"]"""
JATS_XPATHS[
    "pub-date-format"] = """//article-meta/pub-date[@publication-format="{pubtype}"]"""
JATS_XPATHS["pub-date-year"] = JATS_XPATHS["pub-date"] + """/year/text()"""
JATS_XPATHS[
    "primary_id"] = """//article-meta/article-id[@pub-id-type="publisher-id"]/text()"""
JATS_XPATHS[
    "other_ids_doi"] = """//article-meta/article-id[@pub-id-type="doi"]/text()"""
JATS_XPATHS["article-title"] = "//article-meta/title-group/article-title"
JATS_XPATHS[
    "journal-id"] = """//journal-meta/journal-id[@journal-id-type="{journaltype}"]/text()"""
JATS_XPATHS[
    "journal-issn"] = """//journal-meta/issn[@pub-type="{pubtype}"]/text()"""
JATS_XPATHS[
    "journal-issn-pformat"] = """//journal-meta/issn[@publication-format="{pubtype}"]/text()"""
JATS_XPATHS["journal-volume"] = """//article-meta/volume/text()"""
JATS_XPATHS["journal-issue"] = """//article-meta/issue/text()"""
JATS_XPATHS["journal-start_page"] = """//article-meta/fpage/text()"""
JATS_XPATHS["journal-end_page"] = """//article-meta/lpage/text()"""
JATS_XPATHS[
    "publisher-name"] = """//journal-meta/publisher/publisher-name/text()"""
JATS_XPATHS[
    "publisher-place"] = """//journal-meta/publisher/publisher-loc/text()"""
JATS_XPATHS["article-persons"] = """//article-meta/contrib-group/contrib"""
JATS_XPATHS[
    "article-copyright"] = """//article-meta/permissions/copyright-statement/text()"""
JATS_XPATHS[
    "article-license-type"] = """//article-meta/permissions/license/@license-type"""
JATS_XPATHS[
    "article-custom-meta"] = """//article-meta/custom-meta-group/custom-meta/meta-name"""
JATS_XPATHS[
    "article-oa-license"] = """//article-meta/permissions/license[contains(@xlink:href, 'creativecommons.org')]"""
JATS_XPATHS[
    "affiliation"] = """//article-meta/contrib-group/aff[@id="{rid}"]"""
JATS_XPATHS["abstracts-lang_code"] = "//article-meta/abstract/@xml:lang"
JATS_XPATHS["abstracts"] = "//article-meta/abstract"
JATS_XPATHS["abstracts-sec"] = "//article-meta/abstract/sec"
JATS_XPATHS["abstracts-sec-node"] = ".//sec"
JATS_XPATHS["subjects-lang_code"] = "//article-meta/kwd-group/@xml:lang"
JATS_XPATHS["subjects"] = "//article-meta/kwd-group"


@implementer(IArticle)
class JatsArticle:
    """Convert a JATS XML File to a JSON object

    Parameters
    ----------
    dom : etree._ElementTree
        ElementTree
    pubtype : string

    iso639 : vzg.jconv.langcode.ISO_639

    publisher : string
        Set or override the publisher entry

    Returns
    -------
    None
    """
    def __init__(self, dom, pubtype, iso639=None, publisher=None):
        self.dom = dom
        self.iso639 = ISO_639() if isinstance(iso639, type(None)) else iso639
        self.pubtype = pubtype
        self.publisher = publisher

    @property
    def abstracts(self):
        """Article abstracts"""

        logger = logging.getLogger(__name__)

        abstracts = []
        langkey = f"{{{NAMESPACES['xml']}}}lang"

        for node in self.xpath(JATS_XPATHS["abstracts"]):
            abstract = {'text': ""}
            atext = []

            try:
                abstract["lang_code"] = self.iso639.i1toi2[
                    node.attrib[langkey]]
            except IndexError:
                logger.info("abstracts: no lang_code")
            except KeyError:
                logger.info("abstracts: no lang_code")

            secnodes = node.xpath(JATS_XPATHS["abstracts-sec-node"])

            if len(secnodes) == 0:
                nodes = node.xpath("title")
                if len(nodes) > 0:
                    atext.append(node2text(nodes[0]))

                paras = [node2text(para) for para in node.xpath("p")]
                atext += paras
            else:
                for secnode in node.xpath(JATS_XPATHS["abstracts-sec-node"]):
                    nodes = secnode.xpath("title")
                    if len(nodes) > 0:
                        atext.append(node2text(nodes[0]))

                    paras = [node2text(para) for para in secnode.xpath("p")]
                    atext += paras

            atext = [para for para in atext if isinstance(para, str)]
            abstract["text"] += "\n\n".join(atext)

            if len(abstract["text"]) == 0:
                continue

            abstracts.append(abstract)

        return abstracts

    @property
    def copyright(self):
        """Article copyright"""
        logger = logging.getLogger(__name__)
        nodes = self.xpath(JATS_XPATHS['article-copyright'])

        copyr = ""

        try:
            copyr = nodes[0].strip()
        except IndexError:
            logger.info("no copyright")

        return copyr

    @property
    def dateOfProduction(self):
        """Article dateOfProduction"""
        expression = JATS_XPATHS["pub-date"].format(pubtype="pub")
        nodes = self.dom.xpath(expression, namespaces=NAMESPACES)

        if len(nodes) > 0:
            expression = JATS_XPATHS["pub-date-format"].format(
                pubtype=self.pubtype.name)
        else:
            expression = JATS_XPATHS["pub-date"].format(
                pubtype=self.pubtype.value)

        node = self.xpath(expression)

        if len(node) == 0:
            return None

        dateOfProduction = JatsDate(node[0])

        return dateOfProduction

    @property
    def lang_code(self):
        """Article lang_code"""
        logger = logging.getLogger(__name__)
        attributes = self.xpath(JATS_XPATHS['lang_code'])
        lcode = []

        try:
            lcode.append(self.iso639.i1toi2[attributes[0]])
        except IndexError:
            logger.info("no lang_code")
        except KeyError:
            logger.info("no lang_code")

        return lcode

    @property
    def journal_date(self):
        """Look for the earliest date"""
        logger = logging.getLogger(__name__)

        date_node = None

        expression = JATS_XPATHS["pub-date"].format(pubtype="pub")
        nodes = self.dom.xpath(expression, namespaces=NAMESPACES)
        basictype = (len(nodes) > 0)

        for pubtype in JATS_SPRINGER_PUBTYPE:
            if basictype:
                logger.debug("new pub")
                expression = JATS_XPATHS["pub-date-format"].format(
                    pubtype=pubtype.name)
            else:
                expression = JATS_XPATHS["pub-date"].format(
                    pubtype=pubtype.value)

            node = self.dom.xpath(expression, namespaces=NAMESPACES)

            if len(node) > 0:
                dnode = JatsDate(node[0])

                if isinstance(date_node, JatsDate):
                    if dnode.todate() < date_node.todate():
                        date_node = dnode
                else:
                    date_node = dnode

        return date_node

    @property
    def journal(self):
        """Article journal"""
        logger = logging.getLogger(__name__)

        pdict = {"title": "", "year": "", "journal_ids": []}

        jids = {
            'emerald':
            [JATS_XPATHS["journal-id"].format(journaltype="publisher")],
            'springer':
            [JATS_XPATHS["journal-id"].format(journaltype="publisher-id")],
            'doi': [JATS_XPATHS["journal-id"].format(journaltype="doi")],
            self.pubtype.value: [
                JATS_XPATHS["journal-issn"].format(pubtype=self.pubtype.value),
                JATS_XPATHS["journal-issn-pformat"].format(
                    pubtype=self.pubtype.name)
            ]
        }

        expression = JATS_XPATHS["journal-title"]
        node = self.xpath(expression)
        try:
            pdict['title'] = node[0].strip()
        except IndexError:
            logger.info("no journal title")

        date_node = self.journal_date

        if isinstance(date_node.month, int):
            pdict["month"] = f"{date_node.month:02}"
            if isinstance(date_node.day, int):
                pdict["day"] = f"{date_node.day:02}"

        if isinstance(date_node.year, int):
            pdict["year"] = f"{date_node.year}"

        for jtype, expressions in jids.items():

            for expression in expressions:
                node = self.xpath(expression)

                if len(node) == 0:
                    msg = f"no {jtype} journal_id ({self.pubtype.value})"
                    logger.info(msg)
                    continue

                jid = {'type': jtype, 'id': node[0]}

                if jid['type'] in JATS_SPRINGER_JOURNALTYPE.__members__:
                    jid['type'] = JATS_SPRINGER_JOURNALTYPE[jid['type']].value

                pdict["journal_ids"].append(jid)

        publisher = {}

        expression = JATS_XPATHS["publisher-name"]
        node = self.xpath(expression)
        try:
            publisher['name'] = node[0].strip()
        except IndexError:
            logger.info("no publisher name")

        expression = JATS_XPATHS["publisher-place"]
        node = self.xpath(expression)
        try:
            publisher['place'] = node[0].strip()
        except IndexError:
            logger.info("no publisher place")

        if len(publisher) > 0:
            pdict["publisher"] = publisher

        jdata = {
            "journal-volume": "volume",
            "journal-issue": "issue",
            "journal-start_page": "start_page",
            "journal-end_page": "end_page"
        }

        for xkey, attr in jdata.items():
            expression = JATS_XPATHS[xkey]
            node = self.xpath(expression)
            try:
                pdict[attr] = node[0]
            except IndexError:
                logger.info(f"no journal {attr}")

        return pdict

    @property
    def jdict(self):
        """"""
        jdict = {
            "abstracts": self.abstracts,
            "copyright": self.copyright,
            "lang_code": self.lang_code,
            "journal": self.journal,
            "persons": self.persons,
            "primary_id": self.primary_id,
            "other_ids": self.other_ids,
            "subject_terms": self.subjects,
            "title": self.title
        }

        if isinstance(self.dateOfProduction, JatsDate) \
                and isinstance(self.journal_date, JatsDate):
            if self.dateOfProduction.todate() != self.journal_date.todate():
                jdict["dateOfProduction"] = str(self.dateOfProduction)

        if self.pubtype.value == JATS_SPRINGER_PUBTYPE.electronic.value:
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
            logger.info(("no other_id (doi)", self.pubtype.value))

        return [pdict]

    @property
    def persons(self):
        """Article persons"""
        from vzg.jconv.utils import getNameOfPerson

        logger = logging.getLogger(__name__)

        persons = []

        expression = JATS_XPATHS["article-persons"]
        nodes = self.xpath(expression)

        for elem in nodes:
            person = getNameOfPerson(elem)

            if person is None:
                continue

            try:
                person['role'] = JATS_SPRINGER_AUTHORTYPE[elem.get(
                    "contrib-type")].value
            except KeyError:
                msg = "unknown authortype"
                logger.info(msg)

            def aff_():
                affdict_ = {}

                try:
                    affiliation = elem.xpath("""xref[@ref-type="aff"]""")[0]
                except IndexError:
                    msg = "no affiliation"
                    logger.info(msg)
                    return None

                rid = affiliation.get("rid")

                if isinstance(rid, type(None)):
                    msg = "no affiliation"
                    logger.info(msg)
                    return None

                aff_expression = JATS_XPATHS["affiliation"].format(rid=rid)

                try:
                    affnode = self.xpath(aff_expression)[0]
                except IndexError:
                    msg = "no affiliation"
                    logger.info(msg)
                    return None

                if isinstance(affnode.find("institution-wrap"),
                              etree._Element):
                    inode = affnode.find("institution-wrap")
                    affdict_['name'] = ""

                    try:
                        affdict_['name'] = inode.xpath(
                            """institution[@content-type="org-name"]/text()"""
                        )[0].strip()
                    except IndexError:
                        msg = "no affiliation name (org-name)"
                        logger.info(msg)

                    try:
                        affdict_['name'] = inode.xpath(
                            """institution/text()""")[0].strip()
                    except IndexError:
                        msg = "no affiliation name"
                        logger.info(msg)

                    if len(affdict_['name'].strip()) == 0:
                        return None

                    affids = []

                    for affid in inode.xpath("""institution-id"""):
                        affiddict = {}

                        affiddict['type'] = affid.get("institution-id-type")
                        affiddict['id'] = affid.text

                        affids.append(affiddict)

                    affdict_["affiliation_ids"] = affids

                    return affdict_

            affdict = aff_()

            if isinstance(affdict, dict):
                person["affiliation"] = affdict

            persons.append(person)

        return persons

    @property
    def primary_id(self):
        """Article primary_id

        The primary_id needs to be extracted from the DOI.
        The publisher-id is not reliable enough.
        """
        logger = logging.getLogger(__name__)

        pdict = {"type": "", "id": ""}

        publisher = self.publisher

        if publisher is None:
            expression = JATS_XPATHS["publisher-name"]
            node = self.xpath(expression)
            try:
                publisher = node[0].strip()
            except IndexError:
                logger.info("no publisher name")

        try:
            pdict['type'] = getPublisherId(publisher)
        except NoPublisherError:
            logger.info("no publisher", exc_info=True)

        expression = JATS_XPATHS["other_ids_doi"]
        node = self.xpath(expression)

        try:
            doi_path = node[0].split("/")
            pdict['id'] = doi_path[-1]

            if self.pubtype.value == JATS_SPRINGER_PUBTYPE.print.value:
                pdict['id'] += "-p"
            elif self.pubtype.value == JATS_SPRINGER_PUBTYPE.electronic.value:
                pdict['id'] += "-e"

            return pdict
        except (IndexError, ValueError):
            logger.info("primary_id: no doi")

        expression = JATS_XPATHS["primary_id"]
        node = self.xpath(expression)

        try:
            pdict['id'] = node[0]

            if self.pubtype.value == JATS_SPRINGER_PUBTYPE.print.value:
                pdict['id'] += "-p"
            elif self.pubtype.value == JATS_SPRINGER_PUBTYPE.electronic.value:
                pdict['id'] += "-e"
        except IndexError:
            logger.info("no primary_id")

        return pdict

    @property
    def subjects(self):
        """Article subject_terms"""
        logger = logging.getLogger(__name__)

        subjects = []

        def form_():
            """"""
            attributes = self.xpath(JATS_XPATHS["subjects-lang_code"])

            subject = {'scheme': "form", "terms": [], "lang_code": ""}

            try:
                subject["lang_code"] = self.iso639.i1toi2[attributes[0]]
            except IndexError:
                logger.info("no lang_code")
                return subject
            except KeyError:
                logger.info("no lang_code")
                return subject

            for node in self.xpath(JATS_XPATHS["article-custom-meta"]):
                if node.text == "article-type":
                    pnode = node.getparent()
                    subject["terms"].append(pnode.find('meta-value').text)
                    break

            return subject

        # Most likely publisher specific
        subject = form_()

        if len(subject["lang_code"]) > 0 and len(subject["terms"]) > 0:
            subjects.append(subject)

        expression = JATS_XPATHS["subjects"]
        subjext_exp = ".//kwd/text()"
        scheme_exp = ".//title"

        for groupnode in self.xpath(expression):
            title = groupnode.attrib.get("kwd-group-type", None)

            try:
                title = node2text(groupnode.xpath(scheme_exp)[0])
            except IndexError:
                pass

            if title is None:
                continue

            try:
                lang_code = self.iso639.i1toi2[groupnode.xpath(
                    "@xml:lang", namespaces=NAMESPACES)[0]]
            except IndexError:
                continue

            subject = {
                'scheme': "group" if title == "Keywords" else title,
                "terms": [],
                "lang_code": lang_code
            }

            for node in groupnode.xpath(subjext_exp):
                subject["terms"].append(node)

            if len(subject["lang_code"]) > 0 \
                    and len(subject["scheme"]) > 0 \
                    and len(subject["terms"]) > 0:
                subjects.append(subject)

        return subjects

    @property
    def title(self):
        """Article title"""
        logger = logging.getLogger(__name__)

        expression = JATS_XPATHS["article-title"]

        try:
            node = self.xpath(expression)[0]
        except IndexError:
            logger.info("no title")
            return ""

        return node2text(node)

    @property
    def urls(self):
        """Article URLs"""
        logger = logging.getLogger(__name__)

        udict = {}

        expression = JATS_XPATHS["other_ids_doi"]

        try:
            doi = self.xpath(expression)[0]
        except IndexError:
            logger.info("no doi (url)")
            return []

        udict["url"] = f"https://dx.doi.org/{doi}"
        udict["scope"] = "34"
        udict["access_info"] = "unknown"

        for node in self.xpath(JATS_XPATHS["article-custom-meta"]):
            if node.text == "open-access":
                pnode = node.getparent()
                if pnode.find('meta-value').text == "true":
                    udict["access_info"] = "OA"
                break

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

    publisher : string
        Set or override the publisher entry

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
    def __init__(self, jatspath, iso639=None, publisher=None, validate=False):
        self.jatspath = jatspath
        self.articles = []
        self.publisher = publisher

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
        logger = logging.getLogger(__name__)

        pubtypes = []

        expression = JATS_XPATHS["pub-date"].format(pubtype="pub")
        nodes = self.dom.xpath(expression, namespaces=NAMESPACES)
        basictype = (len(nodes) > 0)

        for entry in JATS_SPRINGER_PUBTYPE:
            if basictype:
                logger.debug("new pub")
                expression = JATS_XPATHS["pub-date-format"].format(
                    pubtype=entry.name)
            else:
                expression = JATS_XPATHS["pub-date"].format(
                    pubtype=entry.value)

            nodes = self.dom.xpath(expression, namespaces=NAMESPACES)

            if len(nodes) > 0:
                pubtypes.append(entry)

        logger.debug(pubtypes)

        return pubtypes

    def run(self):
        """"""
        logger = logging.getLogger(__name__)

        for pubtype in self.pubtypes:
            article = JatsArticle(self.dom, pubtype, self.iso639,
                                  self.publisher)

            if self.validate:
                try:
                    jsonschema.validate(instance=article.jdict,
                                        schema=JSON_SCHEMA)
                    self.articles.append(article)
                except jsonschema.ValidationError as Exc:
                    logger.info(Exc, exc_info=False)
                    self.validation_failed = True

                continue

            self.articles.append(article)
