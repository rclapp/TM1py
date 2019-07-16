# -*- coding: utf-8 -*-

import json
from TM1py.Exceptions import TM1pyException
from TM1py.Services.ObjectService import ObjectService


class GitService(ObjectService):
    """ Service to handle Object Updates for Git Integration

    """

    def __init__(self, rest):
        super().__init__(rest)

    def git_init(self, **kwargs):

        request = "/api/v1/GitInit"
        payload = json.dumps(kwargs, ensure_ascii=False)
        response = self._rest.POST(
            request=request,
            data=payload)
        return response

    def git_uninit(self, force=False):
        request = "/api/v1/GitUninit"
        payload = json.dumps({"Force":force})
        response = self._rest.POST(
            request=request,
            data=payload)
        return response

    def git_status(self, username, password):
        request = "/api/v1/GitStatus"
        payload = json.dumps({"Username":username, "Password":password})
        response = self._rest.POST(request=request, data=payload)
        return response

    def git_pull(self, branch, execute_mode, username, password, force=False):
        request = "/api/v1/GitPull"
        payload = json.dumps({
            "Branch": branch,
            "ExecuteMode": execute_mode,
            "Username": username,
            "Password": password,
            "Force": force})
        response = self._rest.POST(request=request, data=payload)
        return response


    def git_push(self, **kwargs):
        request = "/api/v1/GitPush"
        payload = json.dumps(kwargs)
        response = self._rest.POST(request=request, data=payload)
        return response


    def git_execute_plan(self, git_plan_id):
        request = "/api/v1/GitPlans('{}')/tm1.Execute".format(git_plan_id)
        response = self._rest.POST(request=request)
        return response

    def git_deploy(self, url, deployment, branch, username, password, force=False):
        request = "/api/v1/GitPush"
        payload = json.dumps({
            "URL": url,
            "Branch": branch,
            "Username": username,
            "Password": password,
            "Force": force})
        response = self._rest.POST(request=request, data=payload)
        return response


