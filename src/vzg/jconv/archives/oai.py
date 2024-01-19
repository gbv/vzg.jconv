# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

import codecs
import datetime
import logging
import urllib.request as urllib2
from urllib.parse import urlencode
from oaipmh.client import Client, retrieveFromUrlWaiting
from oaipmh.metadata import MetadataRegistry
from oaipmh.metadata import MetadataReader
from oaipmh.error import NoRecordsMatchError
from typing import Generator
from zope.interface import implementer
from vzg.jconv.gapi import NAMESPACES, OAI_ARTICLES_TYPES
from vzg.jconv.interfaces import IArchive
from vzg.jconv.converter.oai import OAIDCConverter


__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


class OAIClient(Client):

    def __init__(self,
                 base_url: str,
                 metadata_registry: MetadataRegistry = None,
                 credentials: str = None,
                 local_file: bool = False,
                 force_http_get: bool = False):

        super().__init__(base_url,
                         metadata_registry,
                         credentials=credentials,
                         local_file=local_file,
                         force_http_get=force_http_get)

        self.__num_records__ = '0'

    def ListRecords_impl(self, args, tree):
        logger = logging.getLogger(__name__)

        stm = "string(./oai:ListRecords/oai:resumptionToken/@completeListSize)"

        try:
            self.__num_records__ = tree.xpath(stm, namespaces=NAMESPACES)
        except Exception:
            logger.error("No resumptionToken", exc_info=True)

        return super().ListRecords_impl(args, tree)
    
    def makeRequest(self, **kw):
        """Either load a local XML file or actually retrieve XML from a server.
        """
        if self._local_file:
            with codecs.open(self._base_url, 'r', 'utf-8') as xmlfile:
                text = xmlfile.read()
            return text
        else:
            # XXX include From header?
            headers = {'User-Agent': 'pyoai'}
            if self._credentials is not None:
                headers['Authorization'] = 'Basic ' + self._credentials.strip()
            if self._force_http_get:
                request_url = '%s?%s' % (self._base_url, urlencode(kw))
                request = urllib2.Request(request_url, headers=headers)
            else:
                binary_data = urlencode(kw).encode('utf-8')
                request = urllib2.Request(
                    self._base_url, data=binary_data, headers=headers)

            return retrieveFromUrlWaiting(request)


@implementer(IArchive)
class ArchiveOAIDC:

    def __init__(self,
                 baseurl: str,
                 from_date: datetime.datetime,
                 until_date: datetime.datetime,
                 local_file: bool = False,
                 converter_kwargs: dict = {"article_type": OAI_ARTICLES_TYPES.unknown,
                                           "validate": False}) -> None:
        self.baseurl = baseurl
        self.from_date = from_date
        self.until_date = until_date
        self.local_file = local_file
        self.converter_kwargs = converter_kwargs

        self.metadataPrefix = "oai_dc"
        oai_dc_reader = MetadataReader(
            fields={
                'title':       ('textList', 'oai_dc:dc/dc:title/text()'),
                'creator':     ('textList', 'oai_dc:dc/dc:creator/text()'),
                'subject':     ('textList', 'oai_dc:dc/dc:subject/text()'),
                'description': ('textList', 'oai_dc:dc/dc:description/text()'),
                'description_language': ('textList', 'oai_dc:dc/dc:description/@xml:lang'),
                'publisher':   ('textList', 'oai_dc:dc/dc:publisher/text()'),
                'contributor': ('textList', 'oai_dc:dc/dc:contributor/text()'),
                'date':        ('textList', 'oai_dc:dc/dc:date/text()'),
                'type':        ('textList', 'oai_dc:dc/dc:type/text()'),
                'format':      ('textList', 'oai_dc:dc/dc:format/text()'),
                'identifier':  ('textList', 'oai_dc:dc/dc:identifier/text()'),
                'source':      ('textList', 'oai_dc:dc/dc:source/text()'),
                'language':    ('textList', 'oai_dc:dc/dc:language/text()'),
                'relation':    ('textList', 'oai_dc:dc/dc:relation/text()'),
                'coverage':    ('textList', 'oai_dc:dc/dc:coverage/text()'),
                'rights':      ('textList', 'oai_dc:dc/dc:rights/text()')
            },
            namespaces={
                'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
                'dc': 'http://purl.org/dc/elements/1.1/'}
        )

        self.registry = MetadataRegistry()
        self.registry.registerReader('oai_dc', oai_dc_reader)

    @property
    def converters(self) -> Generator[OAIDCConverter, None, None]:
        logger = logging.getLogger(__name__)

        max_articles = self.num_files
        if max_articles > 0:
            i = 0

            client = OAIClient(self.baseurl,
                               self.registry,
                               local_file=self.local_file,
                               force_http_get=True)

            if not self.local_file:
                client.updateGranularity()

            for header, record, other in client.listRecords(metadataPrefix=self.metadataPrefix,
                                                            from_=self.from_date,
                                                            until=self.until_date):
                
                if i >= max_articles:
                    break

                i += 1

                if not record:
                    continue

                if self.converter_kwargs.get('article_type') == OAI_ARTICLES_TYPES.openedition:
                    if not 'article' in record.getField('type'):
                        continue

                try:
                    oiaconv = OAIDCConverter(header,
                                             record,
                                             **self.converter_kwargs)
                except (KeyError,
                        ValueError,
                        IndexError,
                        OSError,
                        TypeError):
                    msg = f"Konvertierungsproblem in {record}"
                    logger.error(msg, exc_info=True)

                    continue

                yield oiaconv

    @property
    def num_files(self) -> int:
        """Number of articles"""
        logger = logging.getLogger(__name__)

        client = OAIClient(self.baseurl,
                           self.registry,
                           local_file=self.local_file,
                           force_http_get=True)

        if not self.local_file:
            client.updateGranularity()

        try:
          client.listRecords(metadataPrefix=self.metadataPrefix,
                             from_=self.from_date,
                             until=self.until_date)

        except NoRecordsMatchError:
          msg = f"Keine Records gefunden"
          logger.error(msg)
          return 0

        return int(client.__num_records__)
