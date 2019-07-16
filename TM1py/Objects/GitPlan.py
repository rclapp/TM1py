from TM1py.Objects.TM1Object import TM1Object


class GitPlan(TM1Object):
    """ Abstraction of TM1 Git Remote Object

    """

    def __init__(self, id, branch, force):
        self._id = id
        self._branch = branch
        self._force = force

    @property
    def id(self):
        return self._id

    @property
    def branch(self):
        return self._branch

    @property
    def force(self):
        return self._force


class GitPullPlan(TM1Object):
    """ Abstraction of TM1 Git Remote Object

    """

    SINGLE_COMMIT = 'SingleCommit'
    MULTIPLE_COMMIT = 'MultipleCommit'

    def __init__(self, commit, operations, execution_mode):

        self._commit = commit
        self._operations = operations
        self._execution_mode = execution_mode


    @property
    def commit(self):
        return self._commit

    @property
    def operations(self):
        return self._operations

    @property
    def execution_mode(self):
        return self._execution_mode


class GitPushPlan(TM1Object):
    """ Abstraction of TM1 Git Remote Object

    """

    def __init__(self, new_branch, new_commit, parent_commit, source_files):
        self._new_branch = new_branch
        self._new_commit = new_commit
        self._parent_commit = parent_commit
        self._source_files = source_files

    @property
    def new_branch(self):
        return self._new_branch

    @property
    def new_commit(self):
        return self._new_commit

    @property
    def parent_commit(self):
        return self._parent_commit

    @property
    def source_files(self):
        return self._source_files



