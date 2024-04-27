#!/usr/bin/env python3
from vitis import _server
from vitis import _project
from vitis import _repo
from vitis import _utils
from vitis import _logger
from vitis import _component
from vitis import _platform
from vitis import _configfile
from vitis import _vcxx
import os
import platform as os_platform

from weakref import WeakValueDictionary
from typing import Callable, Optional
import atexit
import os

__all__ = ("create_client", "dispose")
vitis_client = None

class Singleton(type):
    _instances = WeakValueDictionary()
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        else:
            cls._instances[cls].__init__(*args, **kwargs)

        return cls._instances[cls]

class _Vitis(object, metaclass=Singleton):
    """ Vitis package with all service functions.
    """

    def __init__(self, port, host, workspace):

        try:
            self._serverObj = _server.Server(port, host, workspace)
            self._repoObj = _repo.Repository(self._serverObj)
            self._projObj = _project.Project(self._serverObj)
            self._loggerObj = _logger.Logger(self._serverObj)
            self._hlsComponentObj =_component.HLSComponent(self._serverObj)
            self._aieComponentObj = _component.AIEComponent(self._serverObj)
            self._hostComponentObj = _component.HostComponent(self._serverObj)
            self._platformObj = _platform.Platform(self._serverObj)
            self._vcxxObj = _vcxx.Vcxx(self._serverObj)

        except Exception as e:
            _utils.exception(msg="Vitis Create Client failed", ex=e)

    def info(self):
        """
        info:
            Get client connection information.

        Prototype:
                client.info()

        Arguments:
            None

        Returns:
            Client connection information.

        Examples:
            client.info()
        """
        if (self._serverObj.verify() != True):
            print(f"Connection to Vitis server closed, use create_client() to start Vitis Server.")
            return False
        else:
            print(f"Vitis Server running on port {self._serverObj.serverPort}.")
            return True

    def _check_status(self):
        if (self._serverObj.verify() != True):
            _utils.exception(msg="Connection to Vitis server closed, use create_client() to start Vitis Server.")
        else:
            return True

    """ Workspace Service functions
    """

    def get_workspace(self):

        """
        get_workspace:
            Get current workspace path.

        Prototype:
            workspace_path
                client.get_workspace()

        Arguments:
            None

        Returns:
            Workspace path, empty string if workspace path is not set.

        Examples:
            workspace_path = client.get_workspace()
        """

        return (self._serverObj.getWorkspace())

    def set_workspace(self, path):

        """
        set_workspace:
            Set the given workspace path.

        Prototype:
            client.set_workspace(path = <workspace_location>)

        Required Arguments:
            path = <workspace_location>

        Returns:
            True
                Workspace is successfully set.
            Exception
                Failed to set the workspace.

        Examples:
            client.set_workspace("/home/vitis_project")
        """
        if(path==""):
            _utils.exception(msg=f"Error: set_workspace, invalid workspace path {path}.\n\
            \rPlease provide valid path.", ex_type='ValueError')
        else:
            return (self._serverObj.setWorkspace(os.path.realpath(path)))

    def check_workspace(self):

        """
        check_workspace:
            Check whether workspace is set or not.

        Prototype:
            status = client.check_workspace()

        Arguments:
            None

        Returns:
            True
                Workspace is set.
            Exception
                Workspace is not set.

        Examples:
            status = client.check_workspace()
        """
        return (self._serverObj.checkWorkspaceSet())

    """ Logger Service functions
    """

    def log_level(self, level = None):
        """
        log_level :
            Get or set the log level.

        Prototype:
            status = client.log_level(level = <log_level>)

        Optional Arguments:
            level = log_level
                Log level to be set. If level is not specified, current level
                is returned.

        Returns:
            True
                If log level is set.
            Exception
                If log level cannot be set.
            log-level
                If log level is not specified.

        Examples:
            status = client.log_level()
            status = client.log_level(level="DEBUG")

        """
        return (self._loggerObj.log_level(level))

    """ Project service functions
    """
    def create_sys_project(self, name, platform, template=None):
        """
        create_sys_project:
            Create a system project for the given platform. 
        NOTE: To create an accelerated system project with AIE,
              HLS components, use the template argument.

        Prototype:
            app_proj = client.create_sys_project(name = <proj_name>,
                                            platform = <platform_xpfm_path>,
                                            template = <template_name>**)

        Required Arguments:
            name = <proj_name>
                The name of the system project to be created.
            platform = <platform_path>
                The platform xpfm path for which the project is developed.

        Optional Arguments:
            template = <template_name>
                The template for which the project is created.
                "empty_application" (Default for embedded platforms).
                "empty_accelerated_application" (Default for accelerated platforms)

        Returns:
            System project object else an exception is raised.

        Examples:
            sys_proj = client.create_sys_project(name ="vector_addition", platform = "vck190",
                                         template = "installed_examples/vadd")
            sys_proj = client.create_sys_project(name ="empty_app", platform = "zcu102")

        """
        _projObj = _project.Project(self._serverObj)
        if (template == None):
            template_name = self.get_template(type = "ACCL_APP",name = "empty",platforms = [platform])
            if (template_name == None):
                _utils.exception(msg="create_sys_project: cannot find \'Empty Application\' template \n\
                    \rin pre-defined system project repositories", ex_type='LookupError')
        else:
            template_name = template
        return(_projObj._createSystemProject(name=name, platform=platform, template=template_name))

    def get_sys_project(self, name):
        """
        get_sys_project:
            Get system project object by project name.

        Prototype:
            sys_proj = client.get_sys_project(name = <proj_name>)

        Required Arguments:
            name = <proj_name>
                The name of the system project to be fetched. (string)

        Returns:
            System project object else exception is raised.

        Examples:
            proj_proj = client.get_sys_project(name = "gzip")
        """
        if(not isinstance(name, str)):
            _utils.exception(msg=f"get_sys_project: name = '{name}' is not a string.\n\
                \rSpecify valid project name in string format.")
        _projObj = _project.Project(self._serverObj)
        return (_projObj._getSystemProject(name))

    def clone_sys_project(self, name, new_name):
        """
        clone_sys_project:
            Clone a system project.

        Prototype:
            sys_proj = client.clone_sys_project(name = <proj_name>,
                                                new_name = <new_name>)

        Required Arguments:
            name = <proj_obj>
                Name of the system project to be cloned.

            new_name = <new_name>
                Name for the new project to be created.

        Returns:
            Created system project object else exception is raised.

        Examples:
            client.clone_sys_project(name = "proj1", new_name = "cloned_proj")
        """
        return (self._projObj._cloneSystemProject(name, new_name))

    def delete_sys_project(self, name):
        """
        delete_sys_project:
            Delete the system project by project name.

        Prototype:
            status = client.delete_sys_project(name = <proj_name>)

        Required Arguments:
            name = <proj_name>
                The system project to be deleted. (string)

        Returns:
            True
                Project deleted successfully.
            Exception
                Failed to delete the project.

        Examples:
            status = client.delete_sys_project(name = "gzip")
        """
        if(not isinstance(name, str)):
            _utils.exception(msg=f"delete_sys_project: name = '{name}' is not a string.\n\
                \rSpecify valid project name in string format.")
        return (self._projObj._deleteSystemProject(name))

    def list_sys_projects(self):
        """
        list_sys_projects:
            Get all the system projects in the workspace.

        Prototype:
            app_list = client.list_sys_projects()

        Arguments:
            None

        Returns:
            Array of dictionary, each element containing project name and
            location. Empty list in case no projects in workspace. Exception is
            raised in case of any failure.

        Examples:
            project_list = client.list_sys_projects()
        """
        return (self._projObj._listSystemProjects())

    def set_preference(self, level, device, key, value):
        """
        set_:
            Set preference for the given project.

        Prototype:
            client.set_preference(level = <level>, device = <device_type>,
                               key = <key>, value = <value>)

        Required Arguments:
            level = <level>
                Valid levels are 'USER' and 'WORKSPACE'.

            device = <device_type>
                Valid device types are 'VERSAL', 'ZYNQ' and 'ZYNQMP'.

            key = <key>
                Valid key types are 'SYSROOT', 'KERNELIMAGE', 'ROOTFS'.

            value = <value>
                Value for the key provided.

        Returns:
            True
                Preference set successfully.
            Exception
                Failed to set the preference.

        Examples:
            client.set_preference(level = 'USER',
                                  device = 'VERSAL',
                                  key = 'SYSROOT',
                                  value = 'my_sysroots/versal-xilinx-linux')
        """
        return(self._projObj._setPreference(level, device, key, value))

    def get_preference(self, level, device, key):
        """
        get_preference:
            Get preference for the given project.

        Prototype:
            client.get_preference(level = <level>, device = <device_type>,
                                  key = <key>)

        Required Arguments:

            level = <level>
                Valid levels are 'USER' and 'WORKSPACE'.

            device = <device_type>
                Valid device types are 'VERSAL', 'ZYNQ' and 'ZYNQMP'.

            key = <key>
                Valid key types are 'SYSROOT', 'KERNELIMAGE', 'ROOTFS'.

        Returns:
            Value for the provided key.

        Examples:
            client.get_preference(level = 'USER', device = 'VERSAL',
                                  key = 'SYSROOT')
        """
        return(self._projObj._getPreference(level, device, key))

    """ Platform repository and Application repository Service functions
    """
    def list_platform_repos(self):
        """
        list_platform_repos:
            List the added platforms repositories in the current workspace.

        Prototype:
            list = client.list_platform_repos()

        Arguments:
            None

        Returns:
            List of platform_repos with valid/invalid status.

        Examples:
            list = client.list_platform_repos()
        """
        return (self._repoObj.listPlatformRepos(pathname=""))

    def add_platform_repos(self, platform):
        """
        add_platform_repos:
            Add the platform path(s) to platform repository.

        Prototype:
            status = client.add_platform_repos(platform = <platform_path>)

        Required Arguments:
            platform = <platform_path>
                String/list of platform path(s).

        Returns:
            True
                Platform(s) added successfully.
            Exception
                Failed to add platform(s).

        Examples:
            status = client.add_platform_repos("/home/platform1")
            status = client.add_platform_repos(["/home/platform1",
                                                "/home/platform2"])
        """
        platformList = []
        if(type(platform) == str):
            platformList.append(platform)
        elif (type(platform) == list):
            platformList = platform
        else:
            _utils.exception(msg=f"add_platform_repos: platform = '{platform}' is not a valid string or list. \n\
                \rSpecify platform in string or list format, ex. platform = 'path' or platform = ['path1', 'path2']")
            return
        return (self._repoObj.addRepoPaths(platformList))

    def rescan_platform_repos(self, platform):
        """
        rescan_platform_repos:
            Rescan the given platform path(s) and update the platforms list.
            The user needs to call this function if there are any changes to
            the platform repository paths after adding the paths to platform
            repository.

        Prototype:
            status= client.rescan_platform_repos(platform=<platform_path>)

        Required Arguments:
            platform = <platform_path>
                User can give single platform path as string or multiple
                platform paths as strings list.

        Returns:
            True
                Successfully scanned the repository path(s).
            Exception(s)
                Failed to scan the repository path(s).

        Examples:
            status = client.rescan_platform_repos("/internal_platforms")
            status = client.rescan_platform_repos(["/internal_platforms1",
                                                  "/internal_platforms2"])
        """
        platformList = []
        if(type(platform) == str):
            platformList.append(platform)
        elif (type(platform) == list):
            platformList = platform
        else:
            _utils.exception(msg=f"rescan_platform_repos: platform = '{platform}' is not a valid string or list. \n\
                \rSpecify platform in string or list format, ex. platform = 'path> or platform = ['path1', 'path2']")
            return

        return (self._repoObj.rescanRepoPaths(platformList))

    def delete_platform_repos(self, platform):
        """
        delete_platform_repos:
            Delete the platform path(s) from platform repository.

        Prototype:
            status = client.delete_platform_repos(platform = <platform_path>)

        Required Arguments:
            platform = <platform_path> String/list of platform path(s).

        Returns:
            True
                Platform(s) deleted successfully.
            Exception
                Failed to delete platform(s).

        Examples:
            status = client.delete_platform_repos("/home/platform1")
            status = client.delete_platform_repos(["/home/platform1",
                                                   "/home/platform2"])
        """
        platformList = []
        if(type(platform) == str):
            platformList.append(platform)
        elif (type(platform) == list):
            platformList = platform
        else:
            _utils.exception(msg=f"delete_platform_repos: platform = '{platform}' is not a valid string or list. \n\
                \rSpecify platform in string or list format, ex. platform = 'path> or platform = ['path1', 'path2']")
            return
        return (self._repoObj.deleteRepoPaths(platformList))

    def list_platforms(self):
        """
        list_platforms:
           Get list of platform xpfm paths.

        Prototype:
            list = client.list_platforms()

        Arguments:
            None

        Returns:
            List of platforms with xpfm file path with flow and family
            information.

        Examples:
            list = client.list_platforms()
        """
        return (self._repoObj.listPlatforms(platformName=""))

    # TODO: Implement get_platforms method and delete get sw and hw_platform

    def get_sw_platform(self,  xpfm_platform_path):
        """
        get_sw_platform:
            Display software platform information of given platform.

        Prototype:
            list = client.get_sw_platform(platform_xpfm_path = <platform_path>)

        Arguments:
            platform_xpfm_path = <platform_path>

        Returns:
            List of software platform information of given platform,
            else an exception is raised.

        Examples:
            list = client.get_sw_platform("vck190")

        """
        if(not isinstance(xpfm_platform_path, str)):
            _utils.exception(msg=f"get_sw_platform: '{xpfm_platform_path}' is not a valid .xpfm file.\n\
                    \rSpecify a valid xpfm file as string, ex. 'vck190.xpfm'")

        if(os.path.isfile(xpfm_platform_path)):
            if(xpfm_platform_path.endswith(".xpfm")):
                return (self._repoObj.getSwPlatform(pPath=xpfm_platform_path))
            else:
                _utils.exception(msg=f"get_sw_platform: '{xpfm_platform_path}' is not a valid .xpfm file.\n\
                    \rSpecify a valid xpfm file, ex. 'vck190.xpfm'")
        else:
            _utils.exception(msg=f"get_sw_platform: '{xpfm_platform_path}' doesn't exist. \n\
                \rSpecify a valid xpfm platform path")

    def get_hw_platform(self, xpfm_platform_path):
        """
        get_hw_platform:
            Display hardware platform information of given platform.

        Prototype:
            list = client.get_hw_platform(platform_xpfm_path = <platform_path>)

        Arguments:
            platform_xpfm_path = <platform_path>
                Provide the platform xpfm path.

        Returns:
            List of hardware platform information of given platform,
            else an exception is raised.

        Examples:
            list = client.get_hw_platform("vck190")
        """
        if(not isinstance(xpfm_platform_path, str)):
            _utils.exception(msg=f"get_hw_platform: '{xpfm_platform_path}' is not a valid .xpfm file.\n\
                    \rSpecify a valid xpfm file as string, ex. 'vck190.xpfm'")

        if(os.path.isfile(xpfm_platform_path)):
            if(xpfm_platform_path.endswith(".xpfm")):
                return (self._repoObj.getHwPlatform(pPath=xpfm_platform_path))
            else:
                _utils.exception(msg=f"get_hw_platform: '{xpfm_platform_path}' is not a valid .xpfm file.\n\
                    \rSpecify a valid xpfm file, ex. 'vck190.xpfm'")
        else:
            _utils.exception(msg=f"get_hw_platform: '{xpfm_platform_path}' doesn't exist.\n\
                \rSpecify a valid xpfm platform path")

    def get_platform(self, name):
        """
        get_platform:
            Get platform xpfm path matching with provided pattern.

        Prototype:
            xfpm_path = client.get_platform(name = <pattern>)

        Required Arguments:
            name = <pattern>
                String or python supported regular expression.

        Returns:
            Returns first matched platform xpfm path, else returns None.

        Examples:
            xpfm_path = client.get_platform("vck190")
            xpfm_path = client.get_platform("vck190.*dfx")
        """
        return(self._repoObj.getPlatforms(name, firstMatch=True))

    def get_platforms(self, name):
        """
        get_platforms:
            Get list of platform xpfm paths matching with provided pattern.

        Prototype:
            platform_xfpm_list = client.get_platforms(name = <pattern>)

        Required Arguments:
            name = <pattern>
                String or python supported regular expression.

        Returns:
            Returns list of matched platform xpfm paths, else an exception is raised.

        Examples:
            platform_xpfm_list = client.get_platforms("vck190")
            platform_xpfm_list = client.get_platforms("vck190.*dfx")
        """
        return(self._repoObj.getPlatforms(name))
    """
       Application Repository User interface functions.
    """

    def add_local_example_repo(self, name, local_directory, type="ACCL_APP", display_name=None, description= None):
        """
        add_local_example_repo:
            Create a local repository for given type.

        Prototype:
            status = client.add_local_example_repo(name = <app_repo_name>,
                                            local_directory =
                                            <local_repo_directory_path>,
                                            type = <repo_type>**,
                                            display_name =
                                            <repo_display_name>**,
                                            description =
                                            <"Description of repo">**)

        Required Arguments:
            name = <repo_name>
                The local repository name to be added.
            local_directory = <local_repo_directory_path>
                The local repository directory path.

        Optional Arguments:
            type = <repo_type>**
                The repository type.
                Valid types are "ACCL_APP" (Acclerated Applications), "HLS",
                and "AIE". "ACCL_APP" is the default type.
            display_name = <repo_display_name>**
                The repository display name.
            description = <"Description of the repo">**
                The description of the local repository.

        Returns: 
            True
                Successfully added the repository.
            Exception
                Failed to add the repository.

        Examples:
            status = client.add_local_example_repo(name = "test_repo_1", 
                                           local_directory =
                                           "/tmp/test_repo_location",
                                           type = "HLS")
            status = client.add_local_example_repo(name = "test_repo_1",
                                           local_directory =
                                           "/tmp/test_repo_location",
                                           description = "Accel examples
                                           with AIE templates")
        """
        return (self._repoObj.addLocalRepo(name, local_directory, type, display_name, description))

    def add_git_example_repo(self, name, git_url, type="ACCL_APP", git_branch="master", local_directory="", git_tag=None, display_name=None, description= None):

        """
        add_git_example_repo:
            Create a git repository for the given type.

        Prototype:
            status = client.add_git_example_repo(name = <app_repo_name>,
                                             git_url = <git_url>,
                                             type = <repo_type>**,
                                             git_branch = <git_branch_name>**,
                                             git_tag = <git_tag>**,
                                             local_directory =
                                             <local_repo_directory_path>**, 
                                             description = <"Description of the
                                             application repo">**)

        Required Arguments:
            name = <app_repo_name>
                The git repository name to be created.
            git_url = <git_url>
                The git url of the repository.

        Optional Arguments:
            type = <repo_type>**
                The repository type.
                Valid types are "ACCL_APP"(Acclerated Applications), "HLS",
                and "AIE". "ACCL_APP" is the default type.
                The git repository branch name (default: master).
            git_tag = <git_tag>**
                The git repository tag name.
            local_directory = <local_repo_directory_path>**
                The local repository directory path,
            description = <"Description of the repo">**
                The description of the git repository.

        Returns: 
            True
                Successfully added the repo.
            Exception
                Failed to add the repo.

        Examples:
            status = client.add_git_example_repo(name = "accell_examples_master",
                                             git_url = "https://github.com/
                                             Xilinx/Vitis_Accel_Examples.git")
            status = client.add_git_example_repo(name = "accell_examples_master",
                                             git_url = "https://github.com
                                             /Xilinx/Vitis_Accel_Examples.git",
                                             git_branch = "master",
                                             git_tag = "test-tag",
                                             local_directory =
                                             "/tmp/test_git_repo_location",
                                             description =
                                             "Accel examples with AIE
                                             templates")
         """
        return (self._repoObj.addGitRepo(name, url=git_url, type=type, branch=git_branch,
                local_directory=local_directory, tag=git_tag, display_name=display_name, description=description))

    def get_example_repo(self, name):

        """
        get_example_repo:
            Get an existing repository object.

        Prototype:
            app_repo_obj = client.get_example_repo(name = <repo_name>)

        Required Arguments:
            name = <app_repo_name>
                The git repository name.

        Returns:
            Example repository object else an exception is raised.

        Examples:
            app_repo_obj = client.get_example_repo(name="vitis_examples_master")
        """
        return (self._repoObj.getAppRepo(name))

    def list_example_repos(self, type = "ACCL_APP"):
        """
        list_example_repos:
            Get the list of example repositories configured in the tool.

        Prototype:
            status = client.list_example_repos()

        Optional Arguments:
            type = <repo_type>**
                Valid types are "ACCL_APP" (Acclerated Applications) and "HLS",
                "AIE" and "EMBD_APP" (Embedded applications). 
                "ACCL_APP" is the default type.

        Returns:
            List of example repositories with attributes information.

        Examples:
            list = client.list_example_repos("EMBD_APP")
        """
        return (self._repoObj.listAppRepos(repoName=type))

    def delete_example_repo(self, name):
        """
        delete_example_repo:
            Delete given repository from the configured repository
            list.

        Prototype:
            status = client.delete_example_repo(name = <repo_name>)

        Required Arguments: 
            name = <repo_name>
                The repository name.

        Returns:
            True
                Successfully deleted the repository.
            Exception
                Failed to delete the repository.

        Examples:
            status = client.delete_example_repo(name="vitis_examples_master")
        """
        return (self._repoObj.deleteAppRepo(name))

    def reset_example_repo(self, type="ACCL_APP"):
        """
        reset_example_repo:
            Reset the application repositories to tool configured repositories,
            all the user specified given type repositories will be removed.

        Prototype:
            status = client.reset_example_repo(type = <repo_type>)

        Optional Arguments:
            type = <app_repo_type>
                Valid types are "ACCL_APP" (Acclerated Applications) and "HLS",
                "AIE" and "EMBD_APP" (Embedded applications).
                "ACCL_APP" is the default type.

        Returns: 
            True
                Successfully deleted the repository.
            Exception
                Failed to delete the repository.

        Examples:
            status = client.reset_example_repo("ACCL_APP")
            status = client.reset_example_repo("")
        """
        return (self._repoObj.resetAppRepo(type))

    def get_example_repo_state(self, name):
        """
        get_example_repo_state:
            Get the status of given repository.

        Prototype:
            status_str = client.get_example_repo_state(name = <repo_name>)

        Required Arguments: 
            name = <app_repo_name>
                The repository name.

        Returns: 
            The status ("UP_TO_DATE", "NOT_DOWNLOADED" and "NEED_UPDATE") of
            the given application repository.

        Examples:
            status_str = client.get_example_repo_status(name="vitis_examples_master")
        """
        return (self._repoObj.getAppRepoState(name))

    def update_example_repo(self, repo):
        """
        update_app_repo:
            Updates the modified example repository.

        Prototype:
            status = client.update_example_repo(repo = <repo_obj>)

        Required Arguments:
            repo = <app_repo_obj>
                Example repository object, to get example reposit
                object use get_app_repo() function.

        Returns: 
            True
                Successfully updated the repository.
            Exception
                Failed to update the repository.

        Examples:
            status = client.update_example_repo(lib_repo)
        """
        return (self._repoObj.updateAppRepo(appRepo=repo))

    def sync_git_example_repo(self, name):
        """
        sync_git_app_repo:
            Download the git example repository to local directory.

        Prototype:
            status = client.sync_git_example_repo(name = <repo_name>)

        Required Arguments: 
            name = <repo_name>
                The example repository name.

        Returns: 
            True
                Successfully downloaded.
            Exception
                Failed to download.

        Examples:
            status = client.sync_git_example_repo(name = "vitis_examples_master")
        """
        return (self._repoObj.syncGitRepo(name))

    #  Component Methods

    def get_templates(self, type = 'ACCL_APP', name = '', platforms = None):
        """
        get_component_templates:
            Get the required templates from the component repositories.
            Template name filters can be applied optionally.

        NOTE: Please note that accelerated flows are not supported for
              Embedded installer.

        Prototype:
            template_list = client.get_templates(type = <type>,
                                                 name =
                                                 <template_name>,
                                                 platform =
                                                 <"required platforms">**)

        Optional Arguments: 
            type = <type>
                The type for which templates are to be listed.
                Valid types are 'ACCL_APP'(Accelerated applications), 'HLS',
                'AIE', 'EMBD_APP'(Embedded applications).
                'ACCL_APP' is default type.
            name = <template_name>
                The required application template, the name will be matched
                with "display_name" or "hierarchicalname" of template.
            platforms = <required platforms list >**
                Platform(s) that should be supported by the template.
                This is supported only for accelerated applications.

        Returns: 
            The list of matched templates, else returns None.

        Examples:
            template_list = client.get_templates("simple_vadd",
                                                  platforms =
                                                  ["u200", "u280"])
            template_list = client.get_templates('EMBD_APP','hello_world')
        """
        if(type.upper() == 'ACCL_APP'):
            filter = None
            if (platforms != None):
                if isinstance(platforms,str):
                    platforms = [platforms]
                elif isinstance(platforms,list):
                    filter = self._repoObj.createRequisite(supported_platforms_list=platforms)
                else:
                    _utils.exception(msg=f"get_app_templates: platforms = '{platforms}' is not a valid list or string.\n\
                    \rSpecify platforms in list format, ex. 'platforms' = 'vck190' or 'platforms = ['u200', 'u280']'")
            return (self._repoObj.getAppTemplates(name, filter))
        else:
            return (self._repoObj.getComponentTemplates(type, name))

    def get_template(self, type = 'ACCL_APP', name = '', platforms = None):
        """
        get_component_template:
            Get the required templates from the component repositories.
            Template name filters can be applied optionally.

        NOTE: Please note that accelerated flows are not supported for
              Embedded installer.

        Prototype:
            template_list = client.get_template(type = <type>,
                                                name =
                                                <template_name>,
                                                platform =
                                                <"required platforms">**)

        Optional Arguments: 
            component_type = <type>
                The component type for which templates are to be listed.
                Valid types are 'ACCL_APP'(Accelerated applications), 'HLS',
                'AIE', 'EMBD_APP'(Embedded applications).
                'ACCL_APP' is default type.
            name = <template_name>
                The required application template, the name will be matched
                with "display_name" or "hierarchicalname" of template.
            platforms = <required platforms list >**
                Platform(s) that should be supported by the template.
                This is supported only for accelerated applications.

        Returns: 
            The first matched hierarchical name of the template,
            else an exception is raised.

        Examples:
            template_list = client.get_template('EMBD_APP','hello_world')
        """
        if(type.upper() == 'ACCL_APP'):
            templateList = self.get_templates(type, name, platforms)
        else:
            templateList = self.get_templates(type, name)
        if ((templateList != None) and (len(templateList) > 0)):
            return (templateList[0])
        else:
            _utils.exception(msg=f"get_template: cannot find a template matching '{name}'")

    def create_app_component(self, name, platform, domain = None, template = None):
        """
        create_app_component:
            Create an application component.

        Prototype:
            app_comp = client.create_app_component(name = <comp_name>,
                                                    platform = <platform>,
                                                    domain = <domain>,
                                                    template = <template>)

        Required Arguments:
            name = <comp_name>
                Application component name.
            platform = <platform>
                Platform for which component is to be created.
                In case of baremetal platforms, user can specify the domain
                along with platform.

        Optional Argument:
            template = <template>
                Template for the component to be created.
            domain = <domain>
                Specify the domain when there is more than one domain
                on the platform.

        Returns:
            App component object.

        Examples:
            app_comp = client.create_app_component(name = app1,
                                                    platform = platform_xpfm,
                                                    template = 'empty')
        """
        _hostComponentObj = _component.HostComponent(self._serverObj)
        return (_hostComponentObj._createHostComponent(name, platform, domain, template))

    def delete_component(self, name):
        """
        create_delete_component:
            Delete a component.

        Prototype:
            status = client.delete_component(name = <comp_name>)

        Required Arguments:
            name  = <comp_name>
                Component name.

        Returns:
            True
               Component successfully deleted.
            Exception
                Component could not be deleted.

        Examples:
            status = client.delete_component(name = "my_component")
        """
        return (_component.Component._deleteComponent(self._serverObj.channel, name))

    def clone_component(self, name, new_name):
        """
        clone_component:
            Clone a component.

        Prototype:
            comp_obj = client.clone_component(name = <comp_name>,
                                              new_name = <new_name>)

        Required Arguments:
            name = <comp_obj>
                Name of the component to be cloned.

            new_name = <new_name>
                Name for the new component to be created.

        Returns:
            Component object created.

        Examples:
            new_component = client.clone_component(name = "component1", 
                                                   new_name = "component2")
            new_platform = client.clone_component('platform1','new_platform')
        """
        comp = _component.Component._cloneComponent(self._serverObj, name, new_name)

        if(comp.component_type == _component.components_pb2.Component.Type.PL_KERNEL or comp.component_type == _component.components_pb2.Component.Type.HLS):
            _hlsComponentObj = _component.HLSComponent(self._serverObj)
            return(_hlsComponentObj._getHLSComponent(comp))
        elif(comp.component_type == _component.components_pb2.Component.Type.AI_ENGINE):
            _aieComponentObj = _component.AIEComponent(self._serverObj)
            return(_aieComponentObj._getAIEComponent(comp))
        elif(comp.component_type == _component.components_pb2.Component.Type.HOST):
            _hostComponentObj = _component.HostComponent(self._serverObj)
            return(_hostComponentObj._getHostComponent(comp))
        elif(comp.component_type == _component.components_pb2.Component.Type.PLATFORM):
            _platformObj = _platform.Platform(self._serverObj)
            return (_platformObj._clonePlatform(comp))

    def get_component(self, name):
        """
        get_component:
            Get the component object.

        Prototype:
            status = client.get_component(name = <comp_name>)

        Required Arguments:
            name = <comp_name>
                Component name.

        Returns:
            Component object.

        Examples:
            client.get_component(name = 'my_component')
        """
        comp = _component.Component._getComponent(self._serverObj.channel,name)

        if(comp.component_type == _component.components_pb2.Component.Type.PL_KERNEL or comp.component_type == _component.components_pb2.Component.Type.HLS):
            _hlsComponentObj = _component.HLSComponent(self._serverObj)
            return(_hlsComponentObj._getHLSComponent(comp))
        elif(comp.component_type == _component.components_pb2.Component.Type.AI_ENGINE):
            _aieComponentObj = _component.AIEComponent(self._serverObj)
            return(_aieComponentObj._getAIEComponent(comp))
        elif(comp.component_type == _component.components_pb2.Component.Type.HOST):
            _hostComponentObj = _component.HostComponent(self._serverObj)
            return(_hostComponentObj._getHostComponent(comp))

    # TODO: Check with the backend implementation for type
    def list_components(self):
        """
        list_components:
            List all the components in the current workspace.

        Prototype:
            components = client.list_components()

        Arguments:
            None

        Returns:
            List of components in the workspace.

        Examples:
            components = client.list_components()
        """
        return (_component.Component._listComponents(self._serverObj.channel))

    def get_config_file(self, path):
        """
        get_config_file:
            Return an object to read and write a config file.

        Prototype:
            cfg_obj = client.get_config_file(path = <file_path>)

        Required Arguments:
            path = <file_path>
                Path for configuration file.

        Returns:
            Config file object.

        Examples:
            cfg_obj = client.get_config_file(path = "/tmp/file1.cfg")
        """
        _configObj = _configfile.ConfigFileService(self._serverObj)
        return _configObj.config_file(path)

    def create_platform_component(self, name, hw = '', desc = None, os = None, cpu = None, domain_name = None, template = None, no_boot_bsp = False, fsbl_target = None, fsbl_path = None, pmufw_Elf = None,emulation_xsa_path = '', platform_xpfm_path = '', is_pmufw_req = False):
        """
        create_platform_component:
            Create a new platform.

        Prototype:
            platform = client.create_platform_component(name = <platform_name>,
                                              hw = <handoff_file>,
                                              desc = <description>,
                                              os = <os>,
                                              cpu = <processor>,
                                              domain_name = <domain_name>,
                                              template = <template_name>,
                                              no_boot_bsp = <bool>,
                                              fsbl_target = <fsbl_target>,
                                              fsbl_path = <path>,
                                              pmufw_Elf = <path>,
                                              emulation_xsa_path = <xsa_path>,
                                              platform_xpfm_path = <xpfm_path>,
                                              is_pmufw_req = <bool>)

        Required Arguments:
            name = <platform_name>
                Name of the platform.
            hw = <handoff_file>
                Hardware description file to be used to create the
                platform.
            emulation_xsa_path = <xsa_path>
                Path to the Emulation xsa on which the component is created.
            platform_xpfm_path = <xpfm_path>
                Xpfm path of existing platorm.

        Optional Arguments:
            desc = <description>
                Description of the platform.
            os = <os>
                The OS to be used to create the default domain.
            cpu = <processor>
                The processor to be used to create the default domain.
            domain_name = <domain_name>
                Name of the domain to be created in the platform.
            template = <template_name>
                Template for creating domain in case of Baremetal platform.
                "Empty" (Default)
            no_boot_bsp = <bool>
                Mark the platform to build without generating boot components.
            fsbl_target = <fsbl_target>
                Processor-type for which the existing fsbl has to be generated.
                This option is valid only for ZU+. "psu_cortexa53_0" (Default)
            fsbl_path = <path>
                Fsbl path for custom fsbl. This option is used when no_boot_bsp
                is opted.
            pmufw_Elf = <path>
                Prebuilt fsbl.elf to be used as boot component. This option is
                used when no_boot_bsp is opted.
            is_pmufw_req = <bool>
                Mark the platform to create PMU Firmware boot domain. This option
                is false by default.

        Returns:
            Object reference for the newly created platform.

        Examples:
            platform = client.create_platform_component(name = "platform", hw = "zcu102",
                                              cpu = "psu_cortexa53_0",
                                              os = "standalone",
                                              domain_name = "standalone_a53")
        """
        _platformObj = _platform.Platform(self._serverObj)
        return (_platformObj._createPlatform(name, hw, desc, os, cpu, domain_name, template, no_boot_bsp, fsbl_target, fsbl_path , pmufw_Elf, emulation_xsa_path, platform_xpfm_path, is_pmufw_req))

    def get_platform_component(self, name):
        """
        get_platform_component:
            Get the platform object.

        Prototype:
            platform = client.get_platform_component(name = <platform_name>)

        Required Arguments:
            name = <platform_name>
                Name of the platform.

        Returns:
            Plaform object.

        Examples:
            platform = client.get_platform_component(name = "platform")
        """
        _platformObj = _platform.Platform(self._serverObj)
        return (_platformObj._getPlatform(name))

    def delete_platform_component(self, name):
        """
        delete_platform_component:
            Delete the platform.

        Prototype:
            status = client.delete_platform_component(name = <platform_name>)

        Required Arguments:
            name = <platform_name>
                Name of the platform.

        Returns:
            True
                Platform deleted successfully.
            Exception
                Platform could not be deleted.

        Examples:
            status = client.delete_platform_component(name = "platform")
        """
        return (self._platformObj._deletePlatform(name))

    def get_processor_os_list(self, xsa = None, platform = None):
        """
        get_processor_os_list:
            Get os processor list from the xsa path or platform.

        Prototype:
            status = client.get_processor_os_list(xsa = <xsa_path>,
                                                  platform =
                                                  <platform_name>)

        Required Arguments:
            xsa = <xsa_path> or platform = <platform_name>
                XSA or platform from which processor os list is to be
                 extracted.

        Returns:
            List of processor os.

        Examples:
            status = client.get_processor_os_list(name = "platform")
        """
        return (self._platformObj._getProcessorOSList(xsa, platform))

    def list_platform_components(self):
        """
        list_platform_components:
            List all the platform projects in the workspace.

        Prototype:
            platforms = client.list_platform_components()

        Arguments:
            None

        Returns:
            List of platform projects in the workspace.

        Examples:
            platforms = client.list_platform_projects()
        """
        return (self._platformObj._listPlatformComponents())

    def _checkSwRepoPaths(self, repo):
        for swRepoPath in repo:
            if not os.path.exists(swRepoPath):
                _utils.exception(msg=f"Embedded SW Repository path '{swRepoPath}' does not exist.")

    # Software repo commands

    def set_sw_repo(self, level = 'LOCAL', path = None):
        """
        set_sw_repo:
            Set/reset software repo path.
            Setting an empty path will reset the software repo.

        Prototype:
            client.set_sw_repo(level = <'LOCAL'/'GLOBAL'>,
                               path = <repo_path>)

        Required Arguments:                
            path = <repo_path>
                Software repo path to be set.
                Path can be a single path or a list of paths.
                Provide an empty string to reset the software repository paths.
                
        Optional Arguments:
            level = <'LOCAL'/'GLOBAL'>
                Level at which the software repo is to be set.
                LOCAL - 'available to the current workspace'.(Default)
                GLOBAL - 'available across workspaces'.      

        Returns:
            True
                Repo path set successfully.
            Exception
                Failed to set the sw repo path.

        Examples:
            client.set_sw_repo(level = 'GLOBAL', path = '/tmp/test_sw_repo')
                Sets the path as global software repo.
            client.set_sw_repo(level = 'GLOBAL', path = '')
                Resets the software repo.
            
        """
        if(path == None):
            _utils.exception(msg=f"Specify a valid Embedded SW Repository path. \n\
            \rProvide an empty string to reset the repository paths.")
        if(path == ''):
            path = []
        if(type(path) == str):
            path = [path]
        if(path!=[]):
            self._checkSwRepoPaths(path)
        return (self._platformObj._setSwRepo(level = level,path = path))
    
    def remove_sw_repo(self, level = 'LOCAL', path = None):
        """
        remove_sw_repo:
            Remove a software repository from the embedded software repo paths.

        Prototype:
            client.remove_sw_repo(level = <'LOCAL'/'GLOBAL'>,
                                  path = <repo_path>)

        Required Arguments:                
            path = <repo_path>
                Path to be removed from the software repositories.
                Path can be a single path or a list of paths.
                
        Optional Arguments:
            level = <'LOCAL'/'GLOBAL'>
                Software repository level from which path is to be removed.
                LOCAL - 'available to the current workspace'.(Default)
                GLOBAL - 'available across workspaces'.      

        Returns:
            True
                Repo path removed successfully.
            Exception
                Failed to remove the software repo path.

        Examples:
            client.remove_sw_repo(level = 'GLOBAL', path = '/tmp/test_sw_repo')
                Removes the path from the global software repo.
            
        """
        if(path == '' or path == None):
            path = []
        if(type(path) == str):
            path = [path]
        sw_repo_paths = self.get_sw_repo(level)
        new_repo_paths = filter(lambda repo_path: repo_path not in path, sw_repo_paths)
        return (self._platformObj._setSwRepo(level = level,path = list(new_repo_paths)))

    def get_sw_repo(self, level = ''):
        """
        get_sw_repo:
            Get software repository paths.

        Prototype:
            path = client.append_sw_repo(level = <'LOCAL'/'GLOBAL'>)

        Optional Arguments:
            level = <'LOCAL'/'GLOBAL'>
                Level of software repo.
                LOCAL - 'available to the current workspace'.
                GLOBAL - 'available across workspaces'.
                Repositories for both level will be displayed (default).

        Returns:
            Current software repo path.

        Examples:
            client.get_sw_repo(level = 'LOCAL')
                Returns software repositories at workspace level.
            client.get_sw_repo()
                Returns software repositories at both user and workspace level.
        """
        return (self._platformObj._getSwRepo(level = level))
    
    def rescan_sw_repo(self):
        """
        rescan_sw_repo:
            Rescan the software repo paths. The user needs to call this 
            function if there are any changes to the software repository
            paths after adding the paths to software repository.

        Prototype:
            path = client.rescan_sw_repo()

        Arguments:
            None

        Returns:
            True
                Embeddeded software repo paths scanned successfully.
            Exception
                Failed to rescan the software repo paths.

        Examples:
            client.rescan_sw_repo()
        """
        return (self._platformObj._rescanSwRepo())

    def has_vcxx(self) -> bool:
        """
        Check whether the Vitis C++ service is available.

        Returns:
            True if Vitis C++ service available, False if not.
        """
        return self._vcxxObj.has_vcxx()

    def call_vcxx(
            self,
            method_name: str,
            params_json: str,
            log_callback: Optional[Callable[[str, str], None]] = None) -> str:
        """
        Call a method of the Vitis C++ service.

        Arguments:
            method_name
                Name of the Vitis C++ method to call
            params_json
                Parameters for the Vitis C++ method, JSON-encoded string
            log_callback(level: str, message: str)
                Callback function for log messages from Vitis C++

        Returns:
            Result of the Vitis C++ call, JSON-encoded string
        """
        return self._vcxxObj.call_vcxx(method_name, params_json, log_callback)

    def close(self):
        """
        close:
            Close the communication channel to Vitis Server.

        Prototype:
            client.close()

        Returns:
            True
                Successfully closed the communication channel.
            Exception
                Failed to close the channel.

        Examples:
            client.close()
        """
        global vitis_client
        status = False
        if (vitis_client != None):
            print(f"Vitis Client to Server communication channel closed.")
            vitis_client._serverObj.channel.close()
            del vitis_client._serverObj
            del vitis_client._repoObj
            del vitis_client._hlsComponentObj
            del vitis_client._aieComponentObj
            del vitis_client._hostComponentObj
            del vitis_client._projObj
            del vitis_client._loggerObj
            del vitis_client._platformObj
            del vitis_client._vcxxObj
            vitis_client = None
            status = True
        return status

class _Accl_Vitis(_Vitis):
    """
    Client Class for Host Component service.
    """

    def __init__(self, port, host, workspace):
        super().__init__(port, host, workspace)

    def create_hls_component(self, name, cfg_file = None, template = None,):
        """
        create_hls_component:
            Create an HLS component.

        Prototype:
            hls_comp = client.create_hls_component(name = <comp_name>,
                                                    cfg_file = <cfg_file>,
                                                    template = <template>)

        Required Arguments:
            name = <comp_name>
                HLS component name.

        Optional Argument:
            cfg_file = <cfg_file>
                Existing configuration file to be added to the component.
            template = <template>
                Template for the component to be created.

        Returns:
            HLS component object.

        Examples:
            hls_comp = client.create_hls_component(name = my_component,
                                                   cfg_file =
                                                   "/tmp/cfg_files/file1.cfg")
        """
        _hlsComponentObj = _component.HLSComponent(self._serverObj)
        return (_hlsComponentObj._createHLSComponent(name, cfg_file, template))

    def create_aie_component(self, name, platform = None, part = None, template = None):
        """
        create_aie_component:
            Create an AIE component.

        Prototype:
            aie_comp = client.create_aie_component(name = <comp_name>,
                                                   platform = <platform>,
                                                   part = <part>,
                                                   template = <template>)

        Required Arguments:
            name = <comp_name>
                AIE component name.
            platform = <platform> or part = <part>
                Platform/part for which component is to be created. User needs
                to specify only one amongst platform or part.

        Optional Argument:
            template = <template>
                Template for the component to be created.

        Returns:
            AIE component object.

        Examples:
            aie_comp = client.create_aie_component(name = my_component,
                                                    platform = platform_xpfm,
                                                    template = 'empty')
        """
        _aieComponentObj = _component.AIEComponent(self._serverObj)
        if(platform==None and part==None):
            _utils.exception(msg=f"create_aie_component: no platform or part is provided.")
        return (_aieComponentObj._createAIEComponent(name, platform, part, template))

def create_client(port=None, host="localhost", workspace=None):
    """
    create_client:
        Creates client instance

    Prototype:
        client = vitis.create_client(port = <port_number>,
                                       host = <host_name>,
                                       workspace = <workspace_location>)

    Optional Arguments:
        workspace = <workspace_location> Current directory (default)
        port = <port_number>
        host = <hostname> Localhost (default)

    Returns:
        client instance

    Examples:
        client = vitis.create_client()
        client = vitis.create_client(port = 50762, workspace = "/ws1/")
    """
    global vitis_client
    if (os.environ.get('VITIS_EMBEDDED_INSTALL') == "true"):
        vitis_client = _Vitis(port, host, workspace)
        print("Vitis Server for Embedded Edition.", "Only embedded component related functions are supported.")
    else:
        vitis_client = _Accl_Vitis(port, host, workspace)
    if(os_platform.system() == "Windows"):
        vitis_client.log_level('OFF')
    return vitis_client

@atexit.register
def dispose():
    """
    dispose:
        Close all the client connections and force terminate the server.
        If there are any other clients connected to the server, they will no
        longer be functional.

    Prototype:
        dispose()

    Arguments:
        None

    Returns:
        None

    Examples:
        vitis.dispose()
    """
    global vitis_client
    if (vitis_client != None):
        vitis_client._serverObj.stop()
        del vitis_client._serverObj
        del vitis_client._hlsComponentObj
        del vitis_client._aieComponentObj
        del vitis_client._hostComponentObj
        del vitis_client._repoObj
        del vitis_client._projObj
        del vitis_client._loggerObj
        del vitis_client._platformObj
        del vitis_client._vcxxObj
        vitis_client = None
        Singleton._instances.clear()
