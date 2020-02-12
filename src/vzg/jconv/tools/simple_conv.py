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
import logging
from pathlib import Path
import os
from vzg.jconv.converter.jats import JatsConverter

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


def jats(options):
    """Convert JATS files.

    Parameters
    ----------
    options : Namespace
        argparser options

    Returns
    -------
    None
    """
    logger = logging.getLogger(__name__)

    jpath = Path(options.jfiles[0]).absolute()
    opath = Path(options.outdir).absolute()

    if not jpath.is_dir():
        logger.info("No directory")
        return None

    if not opath.exists():
        opath.mkdir(0o755, parents=True)

    for dir_name, subdir_list, file_list in os.walk(jpath):
        logger.info(f'Found directory: {dir_name}')

        relname = dir_name.replace(jpath.as_posix(), '')
        out_newpath = (opath / relname[1:]).resolve()

        for fname in file_list:
            logger.info(f'\t{fname}')

            jatspath = Path(dir_name).absolute() / fname

            jconv = JatsConverter(jatspath, validate=options.validate)
            jconv.run()

            anum = len(jconv.articles)
            msg = f"\t{anum} article(s)"
            logger.info(msg)

            if options.dry_run is False:
                out_newpath.mkdir(0o755, parents=True, exist_ok=True)
                for article in jconv.articles:
                    aname = f"{jatspath.stem}_{article.pubtype}.json"
                    apath = out_newpath / aname

                    with open(apath, "wt") as fh:
                        fh.write(article.json)


def run():
    """Start the application"""
    from argparse import ArgumentParser

    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.WARNING)

    description = "Simple conversion tool."

    parser = ArgumentParser(description=description)

    subparsers = parser.add_subparsers()

    parser_jats = subparsers.add_parser('jats',
                                        help='Convert JATS files')

    parser_jats.add_argument("-n",
                             "--dry-run",
                             dest='dry_run',
                             action='store_true',
                             default=False,
                             help='Do nothing')

    parser_jats.add_argument("-o",
                             "--output-directory",
                             dest="outdir",
                             metavar='Output directory',
                             type=str,
                             default="output",
                             help='Directory of JSON files')

    parser_jats.add_argument(dest="jfiles",
                             metavar='Directory',
                             type=str,
                             nargs=1,
                             help='Directory of JATS files')

    parser_jats.add_argument("--validate",
                             dest='validate',
                             action='store_true',
                             default=False,
                             help='JSON Schema Validation')

    parser_jats.set_defaults(func=jats)

    parser.add_argument("-v",
                        "--verbose",
                        dest='verbose',
                        action='store_true',
                        default=False,
                        help='be verbose')

    options = parser.parse_args()

    if options.verbose:
        logger.setLevel(logging.INFO)

    options.func(options)
