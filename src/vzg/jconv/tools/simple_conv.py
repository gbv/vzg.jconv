# -*- coding: UTF-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2020-2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
import datetime
import logging
import uuid
from pathlib import Path
import zipfile
import tempfile
from vzg.jconv.archives.springer import ArchiveSpringer
from vzg.jconv.archives.oai import ArchiveOAIDC
from vzg.jconv.converter.jats import JatsConverter
from vzg.jconv.converter.oai import OAIDCConverter
from vzg.jconv.gapi import OAI_ARTICLES_TYPES


__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = "plaintext"


def fromarchive(options):
    """Uses a ZIP Archive as source"""
    logger = logging.getLogger(__name__)

    jpath = Path(options.jfiles[0]).absolute()
    opath = Path(options.outdir).absolute()
    dst = opath / jpath.name

    with zipfile.ZipFile(dst, "w") as jsonarchive:
        with zipfile.ZipFile(jpath) as xmlarchive:
            num_xml = 0
            for name in xmlarchive.namelist():
                num_xml += 1

            num_xml = float(num_xml)

            for i, zipinfo in enumerate(xmlarchive.infolist()):
                with tempfile.NamedTemporaryFile("w+b") as tmpfh:
                    tmpfh.write(xmlarchive.read(zipinfo))
                    tmpfh.flush()

                    jatspath = Path(tmpfh.name)
                    zipath = Path(zipinfo.filename)

                    xpercent = i / num_xml * 100
                    msg = f"{zipinfo.filename} ({xpercent:.2f}%)"
                    logger.info(msg)

                    jconv = JatsConverter(jatspath, validate=options.validate)
                    jconv.run()

                    anum = len(jconv.articles)
                    msg = f"\t{anum} article(s)"
                    logger.info(msg)

                    if options.dry_run is False:
                        for article in jconv.articles:
                            aname = f"{zipath.stem}_{article.pubtype}.json"
                            apath = zipath / aname

                            jsonarchive.writestr(
                                apath.as_posix(),
                                article.json,
                                compress_type=zipfile.ZIP_DEFLATED,
                            )

                    if options.stop and jconv.validation_failed:
                        msg = "Validation problem"
                        logger.info(msg)
                        break


def jats(options):
    """Use a ZIP Archive as source."""
    logger = logging.getLogger(__name__)

    jpath = Path(options.jfiles[0]).absolute()
    opath = Path(options.outdir).absolute()
    dst = opath / jpath.name
    deliverysignature = uuid.uuid4()

    if not opath.exists():
        opath.mkdir(0o755, parents=True)

    with zipfile.ZipFile(dst, "w") as jsonarchive:
        converter_kwargs = {"validate": options.validate}
        if options.publisher != "":
            converter_kwargs["publisher"] = options.publisher

        xmlarchive = ArchiveSpringer(jpath, converter_kwargs=converter_kwargs)
        num_xml = float(xmlarchive.num_files)

        for i, jconv in enumerate(xmlarchive.converters):
            xpercent = i / num_xml * 100
            msg = f"{jconv.name} ({xpercent:.2f}%)"
            logger.info(msg)

            jconv.run()

            anum = len(jconv.articles)
            msg = f"\t{anum} article(s)"
            logger.info(msg)

            if options.dry_run is False:
                for j, article in enumerate(jconv.articles):
                    aname = f"{deliverysignature}-{i}-{j}.json"
                    logger.info(aname)
                    jsonarchive.writestr(
                        aname, article.json, compress_type=zipfile.ZIP_DEFLATED
                    )

            if options.stop and jconv.validation_failed:
                msg = "Validation problem"
                logger.info(msg)
                break

            del jconv


def oai(options):
    """Use a OAI responses as source"""
    logger = logging.getLogger(__name__)

    deliverysignature = uuid.uuid4()
    opath = Path(options.outdir).absolute()

    atype = getattr(OAI_ARTICLES_TYPES,
                    options.publisher,
                    OAI_ARTICLES_TYPES.unknown)

    archive = ArchiveOAIDC(options.zippath[0],
                           converter_kwargs={"article_type": atype,
                                             "validate": options.validate})
    num_res = float(archive.num_files)

    for i, conv in enumerate(archive.converters):
        xpercent = i / num_res * 100
        msg = f"{conv.header.identifier} ({xpercent:.2f}%)"
        logger.info(msg)

        conv.run()

        anum = len(conv.articles)
        msg = f"\t{anum} article(s)"
        logger.info(msg)

        if options.dry_run is False:
            for j, article in enumerate(conv.articles):
                aname = f"{deliverysignature}-{i}-{j}.json"
                logger.info(aname)
                jpath = opath / aname

                with jpath.open("w") as jfh:
                    jfh.write(article.json)

        if options.stop and conv.validation_failed:
            msg = "Validation problem"
            logger.info(msg)
            break

        del conv


def run():
    """Start the application"""
    from argparse import ArgumentParser

    description = "Simple conversion tool."

    parser = ArgumentParser(description=description)

    subparsers = parser.add_subparsers()

    parser_oai = subparsers.add_parser(
        "oai", help="Convert OAI responses"
    )

    parser_oai.add_argument(
        "-n",
        "--dry-run",
        dest="dry_run",
        action="store_true",
        default=False,
        help="Do nothing",
    )

    parser_oai.add_argument(
        "-p",
        "--publisher",
        dest="publisher",
        metavar="Publisher",
        type=str,
        required=False,
        default="unknown",
        help="""The name of the publisher. Values: [openedition|cairn]""",
    )

    parser_oai.add_argument(
        "-o",
        "--output-directory",
        dest="outdir",
        metavar="Output directory",
        type=str,
        default="output",
        help="Directory of JSON files",
    )

    parser_oai.add_argument(
        "--stop",
        dest="stop",
        action="store_true",
        default=False,
        help="Stop if JSON Schema Validation fails",
    )

    parser_oai.add_argument(
        "--validate",
        dest="validate",
        action="store_true",
        default=False,
        help="JSON Schema Validation",
    )

    parser_oai.add_argument(
        dest="zippath",
        metavar="Zipfile",
        type=str,
        nargs=1,
        help="Zipfile with OAI records",
    )

    parser_oai.set_defaults(func=oai)

    parser_springer = subparsers.add_parser(
        "jats", help="Convert JATS files from ZIP files"
    )

    parser_springer.add_argument(
        "-n",
        "--dry-run",
        dest="dry_run",
        action="store_true",
        default=False,
        help="Do nothing",
    )

    parser_springer.add_argument(
        "-p",
        "--publisher",
        dest="publisher",
        metavar="Publisher",
        type=str,
        required=False,
        default="",
        help="The name of the publisher, like Springer",
    )

    parser_springer.add_argument(
        "-o",
        "--output-directory",
        dest="outdir",
        metavar="Output directory",
        type=str,
        default="output",
        help="Directory of JSON files",
    )

    parser_springer.add_argument(
        "--stop",
        dest="stop",
        action="store_true",
        default=False,
        help="Stop if JSON Schema Validation fails",
    )

    parser_springer.add_argument(
        "--validate",
        dest="validate",
        action="store_true",
        default=False,
        help="JSON Schema Validation",
    )

    parser_springer.add_argument(
        dest="jfiles",
        metavar="ZIP-File",
        type=str,
        nargs=1,
        help="ZIP file with JATS files",
    )

    parser_springer.set_defaults(func=jats)

    parser.add_argument(
        "--logfile", default="", dest="logfile", metavar="Logfile", type=str, nargs="?"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="be verbose",
    )

    options = parser.parse_args()

    logger = logging.getLogger()

    loghandler = logging.StreamHandler()

    if len(options.logfile.strip()) > 0:
        lpath = Path(options.logfile.strip()).absolute()
        loghandler = logging.FileHandler(lpath)

    logger.addHandler(loghandler)
    logger.setLevel(logging.WARNING)

    if options.verbose:
        logger.setLevel(logging.INFO)

    options.func(options)
