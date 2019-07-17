# -*- coding: utf-8 -*-

import json
from TM1py.Exceptions import TM1pyException
from TM1py.Services.ObjectService import ObjectService
from TM1py.Objects.Git import Git
from TM1py.Objects.GitPlan import GitPlan, GitPushPlan, GitPullPlan
from TM1py.Objects.GitRemote import GitRemote
from TM1py.Objects.GitCommit import GitCommit

class GitService(ObjectService):
    """ Service to handle Object Updates for Git Integration

    """

    def __init__(self, rest):
        super().__init__(rest)

    def git_init(self, **kwargs):
        '''
        :param kwargs:
        :return: tm1 git object
        '''

        request = "/api/v1/GitInit"
        payload = json.dumps(kwargs, ensure_ascii=False)
        response = self._rest.POST(
            request=request,
            data=payload)

        git = Git(response.json()["URL"],
                  response.json()["Deployment"],
                  response.json()["DeployedCommit"],
                  response.json()["Remote"])

        return git


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
        '''
        :param branch:
        :param execute_mode:
        :param username:
        :param password:
        :param force:
        :return: git pull plan object
        '''
        request = "/api/v1/GitPull"
        payload = json.dumps({
            "Branch": branch,
            "ExecuteMode": execute_mode,
            "Username": username,
            "Password": password,
            "Force": force})
        response = self._rest.POST(request=request, data=payload)

        id = response.json()['id']
        branch = response.json()['Branch']
        force = response.json()['Force']

        commit = response.json()['Commit']
        operations = response.json()['Operations']
        new_commit = response.json()['NewCommit']
        execute_mode = response.json()['ExecuteMode']

        pull_plan = GitPullPlan(id, branch, force, commit, operations, new_commit, execute_mode)

        return pull_plan


    def git_push(self, **kwargs):
        request = "/api/v1/GitPush"
        payload = json.dumps(kwargs)
        response = self._rest.POST(request=request, data=payload)

        id = response.json()['id']
        branch = response.json()['Branch']
        force = response.json()['Force']

        source_files = response.json()['SourceFiles']
        new_branch = response.json()['NewBranch']
        new_commit = response.json()['NewCommit']
        parent_commit = response.json()['ParentCommit']

        push_plan = GitPushPlan(id , branch, force, new_branch, new_commit, parent_commit,source_files)

        return push_plan


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


