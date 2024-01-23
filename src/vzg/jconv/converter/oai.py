# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

import json
import jsonschema
import logging
from zope.interface import implementer
from vzg.jconv.gapi import JSON_SCHEMA
from vzg.jconv.gapi import OAI_ARTICLES_TYPES
from vzg.jconv.interfaces import IArticle
from vzg.jconv.interfaces import IConverter
from vzg.jconv.langcode import ISO_639

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


@implementer(IArticle)
class OAIArticle_Base:

    def __init__(self, header, record) -> None:
        self.header = header
        self.record = record

        self.iso639 = ISO_639()

    @property
    def abstracts(self) -> str:
        abstracts = []

        if len(self.record.getField('description')) > 0:
            for index, description in enumerate(self.record.getField('description')):
                try:
                    abstracts.append({
                        'lang_code': self.iso639.i1toi2[self.record.getField('description_language')[index]],
                        'text': description
                    })
                except Exception:
                    pass

        return abstracts

    @property
    def date_of_production(self) -> str:
        datestamp = self.header.datestamp
        return f"{datestamp.year}-{datestamp.month:02}-{datestamp.day:02}"

    @property
    def jdict(self):
        """"""
        jdict = {
            "abstracts": self.abstracts,
            "dateOfProduction": self.date_of_production,
            "lang_code": self.lang_code,
            "journal": self.journal,
            "persons": self.persons,
            "primary_id": self.primary_id,
            "subject_terms": self.subject_terms,
            "title": self.title,
            "urls": []
        }

        return jdict

    @property
    def json(self) -> str:
        """"""
        return json.dumps(self.jdict)

    @property
    def lang_code(self) -> list:
        """Article lang_code"""
        lang_code = []

        for language in self.record.getField('language'):
            if language in self.iso639.i2toi1:
                lang_code.append(language)
            else:
                lang_code.append(self.iso639.i1toi2[language])

        return lang_code

    @property
    def persons(self) -> list:
        """Article persons"""
        persons = []

        for creator in self.record.getField('creator'):
            try:
                creatorParts = creator.split(',')
                persons.append({
                    'firstname': creatorParts[1].strip(),
                    'lastname': creatorParts[0].strip(),
                    'fullname': creatorParts[1].strip() + ' ' + creatorParts[0].strip(),
                })
            except IndexError:
                pass

        return persons

    @property
    def primary_id(self) -> dict:
        """Article primary_id
        """
        pdict = {"type": "oai_id", "id": self.header.identifier}

        return pdict

    @property
    def subject_terms(self) -> list:
        """Article subject_terms"""
        subject_terms = []

        for subject in self.record.getField('subject'):
            try:
                subjectTerm = {}

                lang = self.record.getField('language')[0]

                if lang in self.iso639.i2toi1:
                    subjectTerm['lang_code'] = lang
                else:
                    subjectTerm['lang_code'] = self.iso639.i1toi2[lang]

                subjectTerm['scheme'] = 'OpenEdition'
                subjectTerm['terms'] = []
                for subjectPart in subject.split(' / '):
                    subjectTerm['terms'].append(
                        subjectPart
                    )
                subject_terms.append(subjectTerm)
            except IndexError:
                pass

        return subject_terms

    @property
    def title(self) -> str:
        """Article title"""
        try:
            return self.record.getField('title')[0]
        except IndexError:
            pass

        return ''


@implementer(IArticle)
class OAIArticle_Cairn(OAIArticle_Base):

    def __init__(self, header, record) -> None:
        super().__init__(header, record)

    @property
    def copyright(self) -> str:
        """Article copyright"""
        copyright = ""

        try:
            copyright = self.record.getField('rights')[0]
        except IndexError:
            pass

        return copyright

    @property
    def date_of_production(self) -> str:
        date_of_production = ""

        try:
            date_of_production = self.record.getField('date')[0]
        except IndexError:
            pass

        return date_of_production

    @property
    def jdict(self):
        """"""
        jdict = {
            "abstracts": self.abstracts,
            'copyright': self.copyright,
            "dateOfProduction": self.date_of_production,
            "lang_code": self.lang_code,
            "journal": self.journal,
            "persons": self.persons,
            "primary_id": self.primary_id,
            "subject_terms": self.subject_terms,
            "title": self.title,
            "urls": []
        }

        return jdict

    @property
    def journal(self) -> dict:
        journal = {}

        for source in self.record.getField('source'):
            try:
                sourceParts = source.split('|')
                sourceDateParts = sourceParts[3].split('-')
                sourcePagesParts = sourceParts[4].replace('p. ', '').split('-')
                journal = {
                    'day': sourceDateParts[2].strip(),
                    'end_page': sourcePagesParts[1].strip(),
                    'issue': sourceParts[1].replace('° ', '').strip(),
                    'month': sourceDateParts[1].strip(),
                    'start_page': sourcePagesParts[0].strip(),
                    'title': sourceParts[0].strip(),
                    'volume': sourceParts[2].strip(),
                    'year': sourceDateParts[0].strip(),
                }
            except IndexError:
                pass

        return journal

    @property
    def lang_code(self) -> list:
        """Article lang_code"""
        lang_code = []

        for language in self.record.getField('language'):
            lang_code.append(language)

        return lang_code


@implementer(IArticle)
class OAIArticle_Openedition(OAIArticle_Base):

    def __init__(self, header, record) -> None:
        super().__init__(header, record)

    @property
    def journal(self) -> dict:
        """Article journal"""
        journal = {}

        journal['title'] = self.record.getField('publisher')[0]

        recordDateParts = self.record.getField('date')[0].split('-')
        journal['year'] = recordDateParts[0]

        return journal


@implementer(IConverter)
class OAIDCConverter:
    """_summary_
    """

    def __init__(self,
                 header,
                 record,
                 article_type=OAI_ARTICLES_TYPES.unknown,
                 validate: bool = False) -> None:
        self.header = header
        self.record = record
        self.article_type = article_type
        self.validate = validate

        self.articles = []

        self.__article_types__ = {OAI_ARTICLES_TYPES.cairn: OAIArticle_Cairn,
                                  OAI_ARTICLES_TYPES.openedition: OAIArticle_Openedition}

    def run(self) -> None:
        logger = logging.getLogger(__name__)

        # if self.record.getField("type")[-1] != "article":
        #     msg = "No article: {}".format(self.record.getField("type")[-1])
        #     logger.debug(msg)
        #     return None

        article_cls = self.__article_types__.get(self.article_type, None)

        if article_cls is None:
            msg = "No valid article type found: {}".format(
                self.article_type)
            logger.debug(msg)
            return None

        article = article_cls(self.header, self.record)

        if self.validate:
            try:
                jsonschema.validate(
                    instance=article.jdict, schema=JSON_SCHEMA)
                self.articles.append(article)
            except jsonschema.ValidationError as Exc:
                logger.info(Exc, exc_info=False)
                self.validation_failed = True
        else:
            self.articles.append(article)
