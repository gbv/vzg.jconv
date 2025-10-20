# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2025 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

from vzg.jconv.gapi import JSON_SCHEMA
from vzg.jconv.interfaces import IArticle
from vzg.jconv.interfaces import IConverter
from vzg.jconv.langcode import ISO_639
from zope.interface import implementer
import json
import jsonschema
import logging
import pymarc


@implementer(IArticle)
class MarcArticle:
    def __init__(self, record: pymarc.Record) -> None:
        self.record = record
        self.iso639 = ISO_639()

    @property
    def jdict(self):
        jdict = {
            "abstracts": self.abstracts,
            "dateOfProduction": self.date_of_production,
            "journal": self.journal,
            "lang_code": self.lang_code,
            # "other_ids": self.other_ids,
            "persons": self.persons,
            "primary_id": self.primary_id,
            # "subject_terms": self.subject_terms,
            "title": self.title,
            "urls": self.urls,
        }

        return jdict

    @property
    def json(self) -> str:
        return json.dumps(self.jdict)

    @property
    def lang_code(self):
        language = "en"  # default to 'en' if not specified

        marc041 = self.record.get("041")
        if marc041:
            language = marc041.get("a") or "en"

        lang_code = []
        if language in self.iso639.i2toi1:
            lang_code.append(language)
        else:
            lang_code.append(self.iso639.i1toi2[language])

        return lang_code

    @property
    def date_of_production(self) -> str:
        return self.record.pubyear

    @property
    def persons(self) -> list:
        persons = []

        for field in self.record.get_fields("100", "700"):
            try:
                persons.append(
                    {
                        "fullname": field.get_subfields("a")[
                            0
                        ]  # TODO: consider subfield 4 for "aut"
                    }
                )
            except IndexError:
                pass

        return persons

    @property
    def primary_id(self) -> dict:
        pdict = {"type": "unknown", "id": ""}
        for marc024 in self.record.get_fields("024"):
            for marc024a in marc024.get_subfields("a"):
                if marc024a.startswith("urn:"):
                    pdict = {"type": "urn", "id": marc024a}
                    break
                elif marc024a.startswith("oai:"):
                    pdict = {"type": "oai", "id": marc024a}
                    break

                pdict = {"type": "unknown", "id": marc024a}
                break

        if self.record.get("001"):
            # Fallback to 001 if no 024 found
            marc001 = self.record["001"].value()
            pdict = {"type": "unknown", "id": marc001}

        return pdict

    @property
    def title(self) -> str:
        try:
            return self.record.title
        except IndexError:
            pass

        return ""

    @property
    def journal(self) -> dict:
        journal = {}

        for field in self.record.get_fields("490", "500"):
            journal["title"] = field.get_subfields("a")[0]
        journal["year"] = self.record.pubyear
        # journal["volume"] = self.record.get("260", "").get_subfields("b")[0] if self.record.get("260") else ""
        # journal["issue"] = self.record.get("260", "").get_subfields("c")[0] if self.record.get("260") else ""
        # journal["issn"] = self.record.get("022", "").get_subfields("a")[0] if self.record.get("022") else ""
        # if not journal["title"]:
        #     journal["title"] = self.record.get("245", "").get_subfields("a")[0] if self.record.get("245") else ""

        return journal

    @property
    def abstracts(self) -> str:
        abstracts = []

        for field in self.record.get_fields("520"):
            for abstract in field.get_subfields("a"):
                try:
                    abstracts.append(
                        {
                            "lang_code": self.lang_code[
                                0
                            ],  # TODO (?) specific language for abstract denoted?
                            "text": abstract,
                        }
                    )
                except Exception:
                    pass

        return abstracts

    @property
    def urls(self) -> list:
        urls = []
        for field in self.record.get_fields("856"):
            for url in field.get_subfields("u"):
                if not url.startswith("http"):
                    continue
                urls.append(
                    {
                        "access_info": "OA",
                        "scope": "00",  # TODO: define scope
                        "url": url,
                    }
                )

        return urls


@implementer(IConverter)
class MarcConverter:
    def __init__(self, record: pymarc.Record, validate: bool = False):
        self.record = record
        self.validate = validate
        self.validation_failed = False

        self.articles = []

    def run(self) -> None:
        logger = logging.getLogger(__name__)

        article = MarcArticle(self.record)

        if self.validate:
            try:
                jsonschema.validate(instance=article.jdict, schema=JSON_SCHEMA)
                self.articles.append(article)
            except jsonschema.ValidationError as Exc:
                logger.info(Exc, exc_info=False)
                self.validation_failed = True
        else:
            self.articles.append(article)
