# -*- coding: UTF-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2020 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

import sys
import unittest
import logging


logger = logging.getLogger(__name__)
logger.level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestCase(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testMet1(self):
        """Beschreibung"""
        pass


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)
