# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

import pytest
import inspect

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = "plaintext"


@pytest.mark.trylast
def pytest_configure(config):
    terminal_reporter = config.pluginmanager.getplugin("terminalreporter")
    config.pluginmanager.register(
        TestDescriptionPlugin(terminal_reporter), "testdescription"
    )


class TestDescriptionPlugin:
    def __init__(self, terminal_reporter):
        self.terminal_reporter = terminal_reporter
        self.desc = None

    def pytest_runtest_protocol(self, item):
        self.desc = inspect.getdoc(item.obj)

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_logstart(self, nodeid, location):
        if self.terminal_reporter.verbosity == 0:
            yield
        else:
            self.terminal_reporter.write("\n")
            yield
            if self.desc:
                self.terminal_reporter.write(f"\n{self.desc} ")
