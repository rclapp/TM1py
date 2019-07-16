# -*- coding: utf-8 -*-

import collections
import json

from TM1py.Objects.TM1Object import TM1Object


class GitRemote(TM1Object):
    """ Abstraction of TM1 Git Remote Object

    """

    def __init__(self, connected, branches, tags):
        """
        :param url:
        :param deployment:
        :param deployed_commit:
        :param remote:
        """

        self._connected = connected
        self._branches = branches
        self._tags = tags

    @property
    def connected(self):
        return self._connected

    @property
    def branches(self):
        return self._branches

    @property
    def tags(self):
        return self._tags
