# -*- coding: utf-8 -*-

import collections
import json

from TM1py.Objects.GitCommit import GitCommit
from TM1py.Objects.GitRemote import GitRemote
from TM1py.Objects.TM1Object import TM1Object


class Git(TM1Object):
    """ Abstraction of TM1 Git Object

    """

    def __init__(self, url, deployment, deployed_commit, remote):
        """
        :param url:
        :param deployment:
        :param deployed_commit:
        :param remote:
        """

        self._url = url
        self._deployment = deployment
        self._deployed_commit = GitCommit(deployed_commit["ID"], deployed_commit["Summary"],deployed_commit["Author"])
        self._remote = GitRemote(remote["Connected"], remote["Branches"], remote["Tags"])

    @property
    def url(self):
        return self._url

    @property
    def deployment(self):
        return self._deployment

    @property
    def deployed_commit(self):
        return self._deployed_commit

    @property
    def remote(self):
        return self._remote
