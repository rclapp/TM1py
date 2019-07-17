from TM1py.Objects.TM1Object import TM1Object
from TM1py.Services.GitService import GitService

class TM1Project(TM1Object):
    """
    Object representation of a TM1 Project
    """

    def __init__(self,
                 version,
                 name,
                 settings,
                 tasks,
                 objects,
                 ignore,
                 files,
                 deployments,
                 pre_pull,
                 post_pull,
                 pre_push,
                 post_push,
                 dependencies,
                 precondition,
                 link):

        self._version = version
        self._name = name
        self._settings = settings
        self._tasks = tasks
        self._objects = objects
        self._ignore = ignore
        self._files = files
        self._deployments = deployments
        self._pre_pull = pre_pull
        self._post_pull = post_pull
        self._pre_push = pre_push
        self._post_push = post_push
        self._dependencies = dependencies
        self._precondition = precondition
        self._link = link



