# -*- coding: UTF-8 -*-
"""Date utils

##############################################################################
#
# Copyright (c) 2020 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
import datetime

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


class JatsDate:

    def __init__(self, node):
        """Create a date object from a node"""
        self.node = node

    def __str__(self):
        """"""
        dstr = ""

        if isinstance(self.year, int):
            dstr += f"{self.year}"
            if isinstance(self.month, int):
                dstr += f"-{self.month:02}"
                if isinstance(self.day, int):
                    dstr += f"-{self.day:02}"

        return dstr

    def todate(self):
        """"""
        if isinstance(self.month, int):
            if isinstance(self.day, int):
                return datetime.date(self.year, self.month, self.day)
            return datetime.date(self.year, self.month, 1)

        return datetime.date(self.year, 1, 1)

    @property
    def day(self):
        """"""
        xepr = "day/text()"
        try:
            return int(self.node.xpath(xepr)[0])
        except IndexError:
            return None

    @property
    def month(self):
        """"""
        xepr = "month/text()"
        try:
            return int(self.node.xpath(xepr)[0])
        except IndexError:
            return None

    @property
    def year(self):
        """"""
        xepr = "year/text()"
        return int(self.node.xpath(xepr)[0])
