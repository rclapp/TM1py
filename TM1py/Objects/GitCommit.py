# -*- coding: utf-8 -*-

import collections
import json

from TM1py.Objects import TM1Object


class GitCommit(TM1Object):
    """ Abstraction of TM1 Git Object

    """

    def __init__(self, id, summary, author):
        """
        :param id:
        :param summary:
        :param author:
        """
        self._id = id
        self._summary = summary
        self._author = author

    @property
    def id(self):
        return self._id

    @property
    def summary(self):
        return self._summary

    @property
    def author(self):
        return self._author

