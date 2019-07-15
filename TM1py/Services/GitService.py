# -*- coding: utf-8 -*-

import json
from TM1py.Exceptions import TM1pyException
from TM1py.Services import ObjectService


class GitService(ObjectService):
    """ Service to handle Object Updates for Git Integration

    """

    def __init__(self, rest):
        super().__init__(rest)

    def git_init(self, **kwargs):

        request = "/api/v1/GitInit"
        response = self._rest.POST(
            request=request,
            data=json.dumps(**kwargs, ensure_ascii=False))
        return response


