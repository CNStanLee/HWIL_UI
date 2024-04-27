import grpc
import repository_pb2_grpc
import repository_pb2
from google.protobuf.empty_pb2 import Empty
import os
import re
from weakref import WeakValueDictionary
from vitis import _utils
class Singleton(type):
    _instances = WeakValueDictionary()
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        else:
            cls._instances[cls].__init__(*args, **kwargs)

        return cls._instances[cls]

templateList = []

class AppRepo:
    type = ""

    #copy grpc object to wrapper object
    def __init__(self, app_repo):

        self.name = app_repo.id
        self.display_name = app_repo.name
        self.description = app_repo.description
        self.local_directory = app_repo.local_directory
        self.git_url = app_repo.git_url
        self.git_branch = app_repo.git_branch
        if app_repo.type == repository_pb2.RepoType.HLS:
            self.type = "HLS"
        elif app_repo.type == repository_pb2.RepoType.EMBEDDED:
            self.type = "EMBD_APP"
        elif app_repo.type == repository_pb2.RepoType.AI_ENGINE:
            self.type = "AIE"
        else:
            self.type = "ACCL_APP"
        
    def __str__(self) -> str:
        data = f"'name': {self.name}\n"
        data = data + f"'display_name': '{self.display_name}'\n"
        data = data + f"'description': '{self.description}'\n"
        data = data + f"'local_directory': '{self.local_directory}'\n"
        data = data + f"'git_url': '{self.git_url}'\n"
        data = data + f"'git_branch': '{self.git_branch}'\n'type': '{self.type}'"
        return (data)

    def __repr__(self):
        return (self.__str__())

class Repository(object, metaclass=Singleton):
    """
    Client Class for Platform and Application Repository service.
    """

    def __init__(self, serverObj, host='localhost', port = 50051):

        self.host = host
        self.server_port = port
        self.server = serverObj

        self.stub = repository_pb2_grpc.RepositoryServiceStub(self.server.channel)

    def listPlatformRepos(self, pathname = "") -> list((str,str)) :
        try:
            request = repository_pb2.ListRepoPathsRequest(name=pathname)
            repoPaths = self.stub.ListRepoPaths(request)

            repoList = list()
            for repo_path in repoPaths.repo_paths:
                pathType = repo_path.type
                repoState = repo_path.repo_state
                repoStateStr=""
                if (repoState == repository_pb2.RepoPath.RepoState.VALID):
                    repoStateStr = "VALID"
                elif (repoState == repository_pb2.RepoPath.RepoState.INVALID_PATH):
                    repoStateStr = "INVALID_PATH"
                elif (repoState == repository_pb2.RepoPath.RepoState.NO_PLATFORMS):
                    repoStateStr = "NO_PLATFORMS"

                if (pathType == repository_pb2.RepoPath.INSTALL) :
                    repoList.append((repo_path.path, "INSTALL", repoStateStr))
                elif (pathType == repository_pb2.RepoPath.USER):
                    repoList.append((repo_path.path, "USER", repoStateStr))
                else :
                    repoList.append((repo_path.path, "", repoStateStr))
            return repoList
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot list platform repositories", ex=e)

    # Unused
    # def setRepoPaths(self, pathlist):
    #     try:
    #         repoPaths = repository_pb2.RepoPaths()
    #         for pathinfo in pathlist:
    #             repoPaths.repo_paths.add(path=pathinfo)
    #         response = self.stub.SetRepoPaths(repoPaths)
    #         return response
    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg="Cannot set platform repository paths", ex=e)

    def addRepoPaths(self, pathlist):
        try:
            repoPaths = repository_pb2.RepoPaths()
            for pathinfo in pathlist:
                if(os.path.isdir(pathinfo)):
                    repoPaths.repo_paths.add(path=os.path.abspath(pathinfo))
                else:
                   _utils.exception(msg=f"add_platform_repos: platform path '{pathinfo} is not a directory/doesn't exist")
            response = self.stub.AddRepoPaths(repoPaths)
            return response.success
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot add platform repository path", ex=e)

    def rescanRepoPaths(self, pathlist):
        try:
            repoPaths = repository_pb2.RepoPaths()
            for pathinfo in pathlist:
                if(os.path.isdir(pathinfo)):
                    repoPaths.repo_paths.add(path=os.path.abspath(pathinfo))
                else :
                   _utils.exception(msg=f"rescan_platform_repos: platform path '{pathinfo} is not a directory/doesn't exist")
            response = self.stub.ReScanRepos(repoPaths)
            return response.success
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot rescan platform repository path", ex=e)

    def deleteRepoPaths(self, pathlist):
        try:
            repoPaths = repository_pb2.RepoPaths()
            for pathinfo in pathlist:
                if(os.path.isdir(pathinfo)):
                    repoPaths.repo_paths.add(path=pathinfo)
                else :
                   _utils.exception(msg=f"delete_platform_repos: platform path '{pathinfo} is not a directory/doesn't exist")
            response = self.stub.RemoveRepoPaths(repoPaths)
            return response.success
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot delete platform repository path", ex=e)

    def listPlatforms(self, platformName="") -> list((str,str,str)):
        try:
            listRequest = repository_pb2.ListPlatformsRequest(name=platformName)
            response = self.stub.ListPlatforms(listRequest)

            platformList = list()
            for platform in response.platforms:
                flow = platform.flow
                if (flow == repository_pb2.Platform.DATA_CENTER) :
                    flowStr = "DATA_CENTER"
                elif (flow == repository_pb2.Platform.EMBEDDED_ACCEL) :
                    flowStr = "EMBEDDED_ACCEL"
                else :
                    flowStr = "EMBEDDED"

                platformList.append((platform.path,
                                    flowStr,
                                    platform.family))

            return platformList
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot list platform repository paths", ex=e)

    def getPlatforms(self, name, firstMatch=False):
        try:
            platforms = self.listPlatforms()
            xpfmList= []
            for path in platforms:
                if re.search(name.lower(),path[0]):
                    platfomXpfm = path[0]
                    if (firstMatch):
                        return platfomXpfm
                    else :
                        xpfmList.append(platfomXpfm)

            if(len(xpfmList)):
                return xpfmList
        except:
            _utils.exception(msg=f"get_platforms: No valid platform path found for platform '{name}'")

    def getSwPlatform(self, pPath) -> list((str,str,str,str)):
        try:
            platformRequest = repository_pb2.PlatformRequest(platform_path=pPath)
            response = self.stub.GetSwPlatform(platformRequest)

            swPlatformList = list()
            for domain in response.domains:
                domainDict = dict()
                domainDict["domain_name"] = domain.domain_name
                domainDict["processor"] = domain.processor
                domainDict["os"] = domain.os

                swPlatformList.append(domainDict)
            return swPlatformList
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot get SW platform for '{pPath}'", ex=e)

    def getHwPlatform(self, pPath) -> tuple((int, str, str, str)):
        try:
            platformRequest = repository_pb2.PlatformRequest(platform_path=pPath)
            response = self.stub.GetHwPlatform(platformRequest)
            hwPlatformInfo = dict()
            hwPlatformInfo["ddr_count"] = response.ddr_count
            hwPlatformInfo["memory_type"] = response.memory_type
            hwPlatformInfo["memory_size"] = response.memory_size

            return hwPlatformInfo
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot get HW platform for '{pPath}'", ex=e)

    def _convertRepoType(self, strType):
        if strType.upper() == "ACCL_APP":
            repoType = repository_pb2.RepoType.EXAMPLE
        elif strType.upper() == "AIE":
            repoType = repository_pb2.RepoType.AI_ENGINE
        elif strType.upper() == "HLS":
            repoType = repository_pb2.RepoType.HLS
        else :
            repoType = None
        return repoType

    def addLocalRepo(self, name, local_directory, type, display_name=None, description= None):
        try:
            if type.upper() == "ACCL_APP":
                repoType = repository_pb2.RepoType.EXAMPLE
            elif type.upper() == "AIE":
                repoType = repository_pb2.RepoType.AI_ENGINE
            elif type.upper() == "HLS":
                repoType = repository_pb2.RepoType.HLS
            else :
                _utils.exception(msg=f"add_local_example_repo: unknown repository type '{type}', valid types \n\
                    \r are 'HLS', AIE', and 'ACCL_APP'(default)")

            if (os.path.isdir(local_directory) == False):
                _utils.exception(msg=f"add_local_example_repo: local_directory='{local_directory}' is not a directory/doesn't exist")

            if (display_name == None):
                display_name = name
            appRepo = repository_pb2.AppRepo(id=name,
                                             name=display_name,
                                             description=description,
                                             type=repoType,
                                             local_directory=local_directory)

            self.stub.AddAppRepo(appRepo)
            return True
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot add local repository", ex=e)

    def addGitRepo(self, name, url, type, branch, local_directory, tag, display_name=None, description= None):
        try:
            repoType = self._convertRepoType(type)
            if(repoType == None):
                _utils.exception(msg=f"add_git_example_repo: unknown repository type '{type}', valid types \n\
                    \r are 'HLS', AIE', and 'ACCL_APP' (default)")

            if (display_name == None):
                display_name = name

            appRepo = repository_pb2.AppRepo(id=name,
                                             git_url=url,
                                             type=repoType,
                                             git_branch=branch,
                                             local_directory=local_directory,
                                             name=display_name,
                                             description=description)

            self.stub.AddAppRepo(appRepo)
            return True
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot add git repository", ex=e)

    def getAppRepo(self, name, errorStr=True):
        try:
            appRepoRequest = repository_pb2.GetAppRepoRequest(repo_id = name)
            app_repo = self.stub.GetAppRepo(appRepoRequest)
            return AppRepo(app_repo)

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot get repository", ex=e)

    def listAppRepos(self, repoName="ACCL_APP") -> list((str,str,str,str,str,str,str)):
        try:
            listAppRepoList = list()
            if repoName == "HLS":
                response = self.stub.ListHlsExampleRepos(Empty())
            elif repoName == "AIE":
                response = self.stub.ListAieExampleRepos(Empty())
            elif repoName == "ACCL_APP":
                appRepoRequest = repository_pb2.ListAppRepoRequest(name = "")
                response = self.stub.ListAppRepos(appRepoRequest)
            else :
                _utils.exception(msg=f"list_example_repos: unknown repository type '{type}', valid types \n\
                \r are 'HLS', AIE', and 'ACCL_APP'(default)")

            for app_repo in response.app_repos:
                repoDict = dict()
                repoDict["name"] = app_repo.id
                repoDict["display_name"] = app_repo.name
                repoDict["description"] = app_repo.description
                repoDict["local_directory"] = app_repo.local_directory
                repoDict["git_url"] = app_repo.git_url
                repoDict["git_branch"] = app_repo.git_branch
                repoDict["type"] = repoName
                listAppRepoList.append(repoDict)

            return listAppRepoList
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot list app repositories", ex=e)

    def deleteAppRepo(self, name) -> str:
        try:
            appRepo = self.getAppRepo(name, errorStr= False)
            repoType = self._convertRepoType(appRepo.type)

            if (repoType == None):
                _utils.exception(msg=f"add_git_repo: unknown repository type '{type}', valid types \n\
                \r are 'HLS', AIE', and 'ACCL_APP'")
            if (appRepo != None):
                app_repo = repository_pb2.AppRepo(id=appRepo.name,
                                                  git_url=appRepo.git_url,
                                                  type=repoType,
                                                  git_branch=appRepo.git_branch,
                                                  local_directory=appRepo.local_directory,
                                                  name=appRepo.display_name,
                                                  description=appRepo.description)
                self.stub.DeleteAppRepo(app_repo)
                return True
            else:
                # TODO: Print the available list of configured list_app_repos.
                _utils.exception(msg=f"delete_app_repo, Invalid application repository '{name}'")
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot delete app repository '{name}'", ex=e)

    def resetAppRepo(self, type) -> str:
        try:
            repoType = self._convertRepoType(type)

            if (repoType == None):
                _utils.exception(msg=f"reset_example_repo: unknown repository type '{type}', valid types \n\
                    \r are 'HLS', AIE', and 'ACCL_APP' (default)")
            resetRequest = repository_pb2.ResetAppReposRequest(repo_type=repoType)
            self.stub.ResetAppRepos(resetRequest)

            return True
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot reset app repo", ex=e)

    def getAppRepoState(self, name) -> str :
        try:
            appRepo = self.getAppRepo(name, errorStr= False)
            repoType = self._convertRepoType(appRepo.type)

            if (repoType == None):
                _utils.exception(msg=f"get_example_repo_state: unknown repository type '{type}', valid types \n\
                \r are 'HLS', AIE', and 'ACCL_APP'")
            if (appRepo != None):
                repoStateRequest = repository_pb2.GetAppRepoStateRequest(repo_id=appRepo.name,
                                                                        repo_type=repoType)
                response = self.stub.GetAppRepoState(repoStateRequest)

                if response.status == 1:
                    sStr = "UP_TO_DATE"
                elif response.status == 2:
                    sStr = "NOT_DOWNLOADED"
                else :
                    sStr = "NEED_UPDATE"

                return sStr
            else:
                _utils.exception(msg=f"get_example_repo_state: application repository '{name}' doesn't exist in Vitis repositories")

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot get app repository state for '{name}'", ex=e)

    def updateAppRepo(self, appRepo) -> str:
        try:
            repoType = self._convertRepoType(appRepo.type)

            if (repoType == None):
                _utils.exception(msg=f"update_app_repo: Repo with type '{appRepo.type}' cannot be updated. \n\
                \r Valid types are 'HLS', AIE', and 'ACCL_APP'")

            app_repo = repository_pb2.AppRepo(id=appRepo.name,
                                              git_url=appRepo.git_url,
                                              type=repoType,
                                              git_branch=appRepo.git_branch,
                                              local_directory=appRepo.local_directory,
                                              name=appRepo.display_name,
                                              description=appRepo.description)
            response = self.stub.UpdateAppRepo(app_repo)
            return True
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot update app repository", ex=e)

    def syncGitRepo(self, name) -> str:
        try:
            appRepo = self.getAppRepo(name, errorStr= False)
            repoType = self._convertRepoType(appRepo.type)

            if (repoType == None):
                _utils.exception(msg=f"sync_git_repo: Repo with type '{appRepo.type}' cannot be updated. \n\
                \r Valid types are 'HLS', AIE', and 'ACCL_APP'")

            if (appRepo != None):
                syncRequest = repository_pb2.SyncLocalRepoRequest(repo_id=appRepo.name,
                                                                  repo_type=repoType)

                self.stub.SyncLocalRepo(syncRequest)
                return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot sync app repository '{name}'", ex=e)
            return False

    def createRequisite(self, supported_platforms_list="",
                              unsupported_platforms_list="",
                              certified_platforms_list="",
                              supported_platform_types_list="",
                              runtimes_list="",
                              os_list=""):
        try:
            requisite = repository_pb2.Requisite(supported_platforms=supported_platforms_list,
                                                 unsupported_platforms=unsupported_platforms_list,
                                                 certified_platforms=certified_platforms_list,
                                                 supported_platform_types=supported_platform_types_list,
                                                 runtimes=runtimes_list,
                                                 os_list=os_list)


            return requisite
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Filter creation for platforms failed", ex=e)

    def getAppTemplateTree(self, templateName, requisite=None):
        try:
            templateTreeRequest = repository_pb2.GetAppTemplateTreeRequest(name=templateName,
                                                                           requisite=requisite)

            response = self.stub.GetAppTemplateTree(templateTreeRequest)
            return response

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Unable to fetch the Vitis template tree for '{templateName}'", ex=e)

    def getTemplateInfo(self, pattern, category):
        templateList = []
        for sub_category in category.categories:
            templateList += self.getTemplateInfo(pattern, sub_category)

        for template in category.templates:
            if (pattern != None):
                if ((re.search(pattern.lower(), template.display_name.lower())) or
                   (re.search(pattern.lower(), template.hierarchical_name.lower()))):
                    templateList.append(template.hierarchical_name)
            else:
                templateList.append(template.hierarchical_name)
        return templateList

    def getAppTemplates(self, name, filter):
        name = re.sub(r'([(+)])', r'\\\1',name)
        tree = self.getAppTemplateTree('', requisite=filter)
        if (tree != None):
            tList = self.getTemplateInfo(name, tree.root_category)
            return tList
        else:
            _utils.exception(msg="Unable to fetch the Vitis template tree from repositories")

    def getComponentTemplates(self, component_type, name):
        name = re.sub(r'([(+)])', r'\\\1',name)
        if(component_type.lower() == 'hls'):
            tree = self.stub.GetHlsExampleTemplateTree(Empty())
        elif(component_type.lower() == 'aie'):
            tree = self.stub.GetAieExampleTemplateTree(Empty())
        elif(component_type.lower() == 'embd_app'):
            tree = self.stub.GetEmbeddedExampleTemplateTree(Empty())
        else:
            _utils.exception(msg="Invalid component type '{component_type}'. \n\
            \r Valid types are 'ACCL_APP'(accelerated applications), 'HLS', \n\
            \r 'AIE', 'EMBD_APP'(Embedded applications)")

        if (tree != None):
            tList = self.getTemplateInfo(name, tree.root_category)
            return tList
        else:
            _utils.exception(msg="Unable to fetch the Vitis template tree from repositories")