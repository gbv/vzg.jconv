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
from setuptools import setup, find_packages
from pathlib import Path

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = "plaintext"


def gc(fname):
    mod_directory = Path(__file__).parent
    fpath = mod_directory / fname
    return fpath.read_text()


setup(
    name="vzg.jconv",
    version=gc("VERSION.txt"),
    author="Marc-J. Tegethoff",
    author_email="tegethoff@gbv.de",
    description="Python library to create JSON Data",
    long_description=gc("README.md"),
    long_description_content_type="text/markdown",
    keywords="VZG Python JSON XML JAST",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU Affero General Public License v3",
    ],
    url="https://github.com/gbv/vzg.jconv",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/vzg.jconv",
        "Source": "https://github.com/gbv/vzg.jconv",
        "Tracker": "https://github.com/gbv/vzg.jconv/issues",
    },
    packages=find_packages("src"),
    include_package_data=True,
    license="GNU Affero General Public License v3",
    package_dir={"": "src"},
    namespace_packages=["vzg"],
    install_requires=["jsonschema", "lxml", "setuptools", "wheel", "zope.interface"],
    zip_safe=False,
    python_requires=">=3.10",
    entry_points={"console_scripts": ["simple-conv = vzg.jconv.tools.simple_conv:run"]},
)
