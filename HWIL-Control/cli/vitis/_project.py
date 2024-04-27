import grpc
import projects_pb2_grpc
import projects_pb2
import utils_pb2
import utils_pb2_grpc
from vitis import _build
from vitis import _utils
import copy
import os


class Project(object):
    """
    Client Class for Vitis Project service.
    """

    def __init__(self, server):

        self._server = server
        self._buildObj = _build.Build(server)

        self.stub = projects_pb2_grpc.ProjectsStub(self._server.channel)
        self.util_stub = utils_pb2_grpc.UtilsServiceStub(self._server.channel)

    def __assign__(self, app_proj):
        self.project_name = app_proj.project_name
        self.project_location = app_proj.project_location
        self.type = app_proj.type
        self.platform = app_proj.platform
        self.components = copy.deepcopy(app_proj.associated_components)

    def __str__(self) -> str:
        data = f"'project_name'    : {self.project_name}\n"
        data = data + f"'project_location': '{self.project_location}'\n"
        data = data + f"'project_type'    : '{self._convert_type(type)}'\n"
        data = data + f"'platform'        : '{self.platform}'\n"
        data = data + f"'components'      :'\n"
        for component in self.components:
            data = data + f"'{component}'\n"
        return (data)

    def __repr__(self):
        return (self.__str__())
    
    def _convert_type(self, type):
        if type == projects_pb2.SystemProject.Type.DATA_CENTER:
            return "DATA_CENTER"
        elif type == projects_pb2.SystemProject.Type.EMBEDDED_ACCEL:
            return "EMBEDDED_ACCEL"
        elif type == projects_pb2.SystemProject.Type.EMBEDDED:
            return "EMBEDDED"
        else :
            return "UNKNOWN"

    def add_cfg_files(self, cfg_files, name = None):
        """
        add_cfg_file:
            Add configuration files to the system project.

        Prototype:
            status = sys_proj.add_cfg_file(cfg_files = ["file1",..]**,
                                      name = <container_name/package>)

        Required Arguments:
            cfg_files = ["file1",..]**
                Configuration files to be associated with the project.

            name = <container_name/package>
                Container name or "PACKAGE" for adding cfg files to package.

        Returns:
            True
                Files added successfully.
            Exception
                File could not be added.

        Examples:
            sys_proj.add_cfg_file(cfg_files = 'sample_cfg.cfg', name = 'container1')
        """

        if(type(cfg_files) != list):
            _utils.exception(msg=f"add_cfg_files: cfg_files = '{cfg_files}' is not a valid list. \n\
                \rSpecify cfg_files in list format, ex. cfg_files = ['config_file1.cfg','config_file1.cfg']")

        try:
            if (len(cfg_files) > 0 and name != None):
                if(name=='PACKAGE'):
                    id = self.project_location + "::" + "PACKAGE"
                else:
                    id = self.project_location + "::" + 'hw_link' + '::' + name
                request = projects_pb2.AddCfgFilesRequest(id = id,
                                                          files = cfg_files,
                                                          save = True)
                response = self.stub.AddCfgFiles(request)
                return response
            else :
                _utils.exception(msg="add_cfg_files: config file list is empty or invalid name.")

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="add_cfg_files failed", ex=e)

    def remove_cfg_files(self, cfg_files, name = None,):
        """
        remove_cfg_file:
            Remove configuration files from the system project.

        Prototype:
            status = sys_proj.remove_cfg_file(cfg_files = ["file1",..]**,
                                              name = <container_name>)

        Required Arguments:

            cfg_files = ["file1",..]**
                Configuration files to be removed from the system project.

        Optional Arguments:
            name = <container_name/package>
                Container name or "PACKAGE" for adding cfg files to package.

        Returns:
            True
                Files removed successfully.
            Exception
                File could not be removed.

        Examples:
            sys_proj.remove_cfg_file(name = 'container1', cfg_files = 'sample_cfg.cfg')
        """
        if(type(cfg_files) != list):
            _utils.exception(msg=f"remove_cfg_files: cfg_files = '{cfg_files}' is not a valid list. \n\
                \rSpecify cfg_files in list format, ex. cfg_files = ['config_file1.cfg','config_file1.cfg']")

        try:
            if (len(cfg_files) > 0 and name != None):
                if(name=='PACKAGE'):
                    id = self.project_location + "::" + "PACKAGE"
                else:
                    id = self.project_location + "::" + 'hw_link' + '::' + name

                request = projects_pb2.RemoveCfgFilesRequest(id = id,
                                                             files = cfg_files,
                                                             save = True)
                response = self.stub.RemoveCfgFiles(request)
                return response
            else :
                _utils.exception(msg="remove_cfg_files: config file list is empty")

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="remove_cfg_files failed", ex=e)

    def import_files(self, files, from_loc, dest_dir_in_cmp = None):
        """
        import_files:
            Import files to the system project.

        Prototype:
            status = sys_proj.import_files(from_loc = <Location of src or
                                            config file(s) path>,
                                            files = ["file1",..]**,
                                            dest_dir_in_cmp = "dst_dir"**)

        Required Arguments:

            from_loc = <Location of src or config file(s) path>
                From The location can be a directory/file, the path can be
                absolute/relative.

            files = ["file1",..]**
                List of files to be imported from the given from_loc path.

            dest_dir_in_cmp = "dst_dir"**
                Destination directory , create if directory doesn't exist.

        Returns:
            True
                Files imported successfully.
            Exception
                File could not be imported.

        Examples:
            sys_proj.import_files(name = "", )
        """
        if(files is not None and type(files) != list):
            _utils.exception(msg=f"import_files: files = '{files}' is not a valid list. \n\
                \rSpecify files in list format, ex. files = ['src_file1.cpp','config_file1.cfg']")
        try:
            if (self.project_location != None):
                from_loc_abs = os.path.abspath(from_loc)
                dest_loc = self.project_location

                if (dest_dir_in_cmp != None):
                    dest_dir = os.path.join(dest_loc, dest_dir_in_cmp)
                    os.makedirs(dest_dir, exist_ok = True)
                    dest_loc = os.path.abspath(dest_dir)
                
                request = utils_pb2.ImportFilesRequest(src_loc = from_loc_abs,
                                                        dest_loc = dest_loc,
                                                        files = files)
                response = self.util_stub.ImportFiles(request)
                return True

            else:
                _utils.exception(msg=f"import_files: Invalid project")

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="import_files failed", ex=e)

    def remove_files(self, files):
        """
        remove_files:
            Remove files from the system project.

        Prototype:
            status = component.remove_files(files = ["file1",..]**)

        Required Arguments:

            files = ["file1",..]**
                List of files to be removed from the component.

        Returns:
            True
                Files imported successfully.
            Exception
                File could not be imported.

        Examples:
            component.remove_files(name = "", )
        """
        if(type(files) != list):
            _utils.exception(msg=f"import_files: files = '{files}' is not a valid list. \n\
                \rSpecify files in list format, ex. files = ['src_file1.cpp','config_file1.cfg']")
        try:
            request = utils_pb2.RemoveFilesRequest(src_loc = self.project_location,
                                                   files = files)
            response = self.util_stub.RemoveFiles(request)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="remove_files failed", ex=e)

    def report(self):
        """
        report:
            Display information of all the matching projects in workspace and
            secondary folders.

        Prototype:
            status = sys_proj.report()

        Returns:
            System project information, error in case given project is not
            part of workspace or secondary folders.

        Examples:
            sys_proj_details = sys_proj.report()
        """
        try:
            if (self.project_location != None):
                getPrjRequest = projects_pb2.GetSystemProjectRequest(project_location=self.project_location)
                appObj = self.stub.GetSystemProject(getPrjRequest)
                if (appObj != None):
                    print(f"project_name       :  '{appObj.project_name}'")
                    print(f"project_location   :  '{appObj.project_location}'")
                    print(f"platform           :  '{appObj.platform}'\n")
                    print(f"Components:")
                    for component in appObj.associated_components:
                        print(f"                    :",component)
                    print(f"Containers:")
                    for container in appObj.link_component.containers:
                        print(f"    container_name :  '{container.container_name}'")
                        print(f"      kernels: ")
                        for item in container.kernels:
                            print(f"        kernel     :  {item}")
                        for cfg in container.cfg_files:
                            print(f"        cfg_files  :  '{cfg}'")

        except OSError as e:
            _utils.exception(msg=f"Invalid system project object '{app_obj}'", ex=e)

    def add_component(self, name, container_name=None):
        """
        add_component:
            Add the specified component to the given system project.

        Prototype:
            component = sys_proj.add_component(name = <component_name>
                                          container_name = <containers_list>)

        Required Arguments:
            name = <component_name>
                The name for the component to be added.

        Optional Argument:
            container_name = <containers_list>
                List of containers at which component is to be added.
                Component is added to the system project. (Default)

        Returns:
            True
                Component is successfully added.
            Exception
                Could not add the component.

        Examples:
            pl_kernels1 = sys_proj.add_component(name = "my_component")
        """
        if(not isinstance(name, str)):
            _utils.exception(msg=f"add_component: name = '{name}' is not a string.\n\
                \rSpecify valid component name in string format.")

        if(container_name is not None and type(container_name) != list):
             _utils.exception(msg=f"add_component: not a valid container list '{container_name}'. \n\
                \rSpecify container_name in list format e.g. container_name = ['binary_container_1'].")

        try:
            location = self._getProjectLocation(name, "add_component")
            request = projects_pb2.AddComponentToSystemRequest(project_location = self.project_location,
                                                                component_location = location,
                                                                containers = container_name,
                                                                save = True)
            response = self.stub.addComponentToSystem(request)
            self.__assign__(response)
            return self

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="add component failed", ex=e)

    def remove_component(self, name):
        """
        remove_component:
            Remove the component from the system project.

        Prototype:
            status = sys_proj.remove_component(name = <component_name>)

        Required Arguments:
            name = <component_name>
                Component name.

        Returns:
            True
                Successfully removed the component.
            Exception
                Failed in removing the component.

        Examples:
            status = sys_proj.remove_component(name = "my_component")
        """
        if(not isinstance(name, str)):
            _utils.exception(msg=f"remove_component: name = '{name}' is not a string.\n\
                \rSpecify valid component name in string format.")

        try:
            location = self._getProjectLocation(name, "add_component")
            request = projects_pb2.RemoveComponentFromSystemRequest(project_location = self.project_location,
                                                                         component_location = location,
                                                                         save = True)
            response = self.stub.removeComponentToSystem(request)
            self.__assign__(response)
            return self

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="remove component failed", ex=e)

    def add_precompiled_kernel(self, xo_file_path, containers):
        """
        add_precompiled_kernel:
            Add precompiled kernel to the container.

        Prototype:
            status = sys_proj.add_precompiled_kernel(
                                            xo_file_path=<output_xo_file_path>,
                                            containers = <container_list>)

        Required Arguments:
                containers = <container_list>
                    List of the containers to which the kernels are to be added.

                xo_file_path = <output_xo_file_path>
                    The path of the output xo file. The file path that will be
                    created by the build command. This path can be build-directory
                    -relative, or could be an absolute path, or could be based on
                    the PROJECT or BUILD macros.
                    "kernel.xo" → <build>/kernel.xo
                    "BUILD/kernel.xo" → <build>/kernel.xo
                    "PROJECT/kernel.xo" → <project>/kernel.xo

            Returns:
                True
                    Successfully added the precompiled kernel.
                Exception
                    Failed to add the user precompiled kernel.

            Examples:
                status = sys_proj.add_precompiled_kernel(xo_file_path=
                                                    './out/custom_kernel.xo',
                                                    containers=['container_1'])
        """

        if(type(containers) != list):
             _utils.exception(msg=f"add_precompiled_kernel: not a valid container list '{containers}'. \n\
                \rSpecify containers in list format e.g. containers = ['binary_container_1'].")

        try:
            kernelObjRequest = projects_pb2.AddPrebuiltBinaryToSystemRequest(
                                                   project_location = self.project_location,
                                                   binary_file_path = xo_file_path,
                                                   containers = containers,
                                                   save = True)
            kernelObjResponse = self.stub.AddPrebuiltBinaryToSystem(kernelObjRequest)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="add_precompiled_kernel failed", ex=e)

    def remove_precompiled_kernel(self, xo_file_path, containers):
        """
        remove_precompiled_kernel:
            Remove precompiled kernel to the container.

        Prototype:
            status = sys_proj.remove_precompiled_kernel(
                                            xo_file_path=<output_xo_file_path>,
                                            containers = <container_list>)

        Required Arguments:
                containers = <container_list>
                    List of the containers to which the kernels are to be added.

                xo_file_path = <output_xo_file_path>
                    The path of the output xo file. The file path that will be
                    created by the build command. This path can be build-directory
                    -relative, or could be an absolute path, or could be based on
                    the PROJECT or BUILD macros.
                    "kernel.xo" → <build>/kernel.xo
                    "BUILD/kernel.xo" → <build>/kernel.xo
                    "PROJECT/kernel.xo" → <project>/kernel.xo

            Returns:
                True
                    Successfully removed the precompiled kernel.
                Exception
                    Failed to remove the user precompiled kernel.

            Examples:
                status = sys_proj.remove_precompiled_kernel(
                                               xo_file_path='./out/custom_kernel.xo',
                                               containers=['container_1'])
        """

        if(type(containers) != list):
             _utils.exception(msg=f"remove_precompiled_kernel: not a valid container list '{containers}'. \n\
                \rSpecify containers in list format e.g. containers = ['binary_container_1'].")

        try:
            kernelObjRequest = projects_pb2.RemovePrebuiltBinaryFromSystemRequest(
                                                   project_location = self.project_location,
                                                   binary_file_path = xo_file_path,
                                                   containers = containers,
                                                   save = True)
            kernelObjResponse = self.stub.RemovePrebuiltBinaryFromSystem(kernelObjRequest)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="add_precompiled_kernel failed", ex=e)

    def add_container(self, name, cfg_file_list=None):
        """
        add_container:
            Add a binary container with given kernels, and config files.

        Prototype:
            status= sys_proj.add_container(name = <container_name>,
                                      cfg_file_list = [cfg_listR]*)

        Required Arguments:
            name = <container_name>
                The name of the container to be created.

        Optional Arguments:
            cfg_file_list = [cfg_list]
                The list of linker config files for the container. The
                cfg_file_list can be updated later using "add_cfg_files" API.

        Returns:
            True
                Successfully added the container.
            Exception
                Failed to add the container.

        Examples:
            status = sys_proj.add_container(name = "container")
        """
        if(cfg_file_list is not None and type(cfg_file_list) != list):
             _utils.exception(msg=f"add_container: not a valid cfg file list '{cfg_file_list}'. \n\
                \rSpecify cfg_file_list in list format e.g. cfg_files = ['config_file1.cfg','config_file2.cfg'].")
        try:
            # container_id = self.project_name + "::" + 'hw_link' + '::' + name
            container_id = self.project_location + "::" + 'hw_link' + '::' + name
            containerObjRequest = projects_pb2.Container(container_id  = container_id,
                                                         container_name  = name,
                                                         cfg_files  = cfg_file_list)

            createContainerRequest = projects_pb2.CreateContainerRequest(container  = containerObjRequest,
                                                                         save = True)
            containerObjResponse = self.stub.CreateContainer(createContainerRequest)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="add_container failed", ex=e)

    def delete_container(self, name):
        """
        delete_container:
            Delete binary container object from the project.

        Prototype:
            status = sys_proj.delete_container (name = <container_name>)

        Required Arguments:
            name = <container_name>
                The name of the container or it can be fetched using
                "list_containers" function".

        Returns:
            True
                Successfully deleted the container.
            Exception
                Failed to delete the container.

        Examples:
            status = sys_proj.delete_container(name = "binary_containter")
        """
        try:
            # containerId = self.project_name + "::" + 'hw_link' + '::' + name
            container_id = self.project_location + "::" + 'hw_link' + '::' + name
            deleteContainerRequest = projects_pb2.DeleteContainerRequest(container_id  = container_id,
                                                                         save = True)
            self.stub.DeleteContainer(deleteContainerRequest)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="delete_container failed", ex=e)

    def list_components(self, type = None):
        """
        list_components:
            List all the components associated with the system project.

        Prototype:
            components = sys_proj.list_components(type = <component_type>)

        Optional Arguments:
            type = <component_type_filter>
                List of component types to return components of specific types.
                Valid types are 'HLS', 'AI_ENGINE' and 'APP'.
                Returns components of all types by default.

        Returns:
            List of components in the system project.

        Examples:
            my_proj.list_components(type = "AI_ENGINE")
        """
        if(not isinstance(type,str) and type!=None):
            _utils.exception(msg=f"list_components: type = '{type} is not a valid string.")
        
        if(type!= None):
            if type.upper() == 'HLS':
                type = projects_pb2.Component.Type.PL_KERNEL
            elif type.upper() == 'AI_ENGINE':
                type = projects_pb2.Component.Type.AI_ENGINE
            elif type.upper() == 'APP':
                type = projects_pb2.Component.Type.HOST
            else:
                _utils.exception(msg=f"list_components: type = '{type} is not a valid component type. \n\
                    \r Valid component types are HLS, AI_ENGINE and EMBD_APP")
            type = [type]
            
        try:
            listComponentRequest = projects_pb2.ListComponentsRequest(project_location = self.project_location,
                                                                      type_filter = type)
            response = self.stub.ListComponents(listComponentRequest)
            return response.component

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="list_components failed", ex=e)

    def update_platform(self, platform):
        """
        update_platform:
            Update the project's platform with new platform. It needs new
            domain mapping to components in the project.

        Prototype:
            sys_proj = sys_proj.update_platform(platform = <new_platform_path>)

        Required Arguments:
            platform = <new_platform_path>
                Xpfm path to the new platform.

        Returns:
            Updated system project object else an exception is raised.

        Example:
            sys_proj = sys_proj.update_platform(platform = 'xilinx_u200.xpfm')
        """

        try:
            if (self.project_location != None):
                updatePrjRequest = projects_pb2.UpdateSystemProjectRequest(project_location=self.project_location,
                                                                                platform=platform)
                updatePrjResponse = self.stub.UpdateSystemProject(updatePrjRequest)
                self.__assign__(updatePrjResponse)
                return self

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot update system project '{self.project_name}'", ex=e)

    def clean(self, target = "sw_emu", comp_name=None):
        """
        clean:
            Clean the given system project for the specified build target.

        Prototype:
            status = sys_proj.clean(target = <target_name>, comp_name = <comp_name>)

        Required Arguments:
            target = <target name> - One of the supported targets
                                     (sw_emu/hw_emu/hw).
            comp_name=<comp_name>**
                Component to be built. Complete system project (default)

        Returns:
            Build Status
                SUCCESS/FAILURE
            Exception
                Failed to clean the system project.

        Examples:
            status = sys_proj.clean(target = "hw")
        """
        if (target == "sw_emu" or target == "hw_emu" or target == "hw"):
            return (self._buildObj.clean_app(self.project_name, target, comp_name))
        else:
            _utils.exception(msg=f"clean: '{target}' not a valid build target. \n\
                \rValid targets are 'sw_emu' or 'hw_emu' or 'hw'", ex_type='ValueError')

    def clean_all(self, target = "sw_emu", comp_name=None):
        """
        clean_all:
            Clean the given system project and it's associated components for the specified build target.

        Prototype:
            status = sys_proj.clean_all(target = <target_name>, comp_name = <comp_name>)

        Required Arguments:
            target = <target name> - One of the supported targets
                                     (sw_emu/hw_emu/hw).
            comp_name=<comp_name>**
                Component to be built. Complete system project (default)

        Returns:
            Build Status
                SUCCESS/FAILURE
            Exception
                Failed to clean the system project.

        Examples:
            status = sys_proj.clean_all(target = "hw")
        """
        if (target == "sw_emu" or target == "hw_emu" or target == "hw"):
            return (self._buildObj.clean_app(self.project_name, target, comp_name, build_target="clean all"))
        else:
            _utils.exception(msg=f"clean_all: '{target}' not a valid build target. \n\
                \rValid targets are 'sw_emu' or 'hw_emu' or 'hw'", ex_type='ValueError')

    def build(self, target = "sw_emu", comp_name = None, build_comps = True):
        """
        build:
            Initiates the build of an system project for the given build
            target.

        Prototype:
            status = sys_proj.build(target= <target name>,
                                   comp_name = <comp_name>**,
                                   build_comps = <bool>)

        Optional arguments:
            target = <target name>
                One of the supported targets (sw_emu/hw_emu/hw).
                sw_emu (Default)
            comp_name = <comp_name>**
                Component to be built. Complete system project (default)
            build_comps = <bool>
                Build the dependent components if they're not built already.
                True (Default).

        Returns:
            Build Status
                SUCCESS/FAILURE
            Exception
                Failed to build the system project.

        Examples:
            status = sys_proj.build(target = "hw")
        """
        if (target == "sw_emu" or target == "hw_emu" or target == "hw"):
            return (self._buildObj.build_app(self.project_name, comp_name, target, build_comps))
        else:
            _utils.exception(msg=f"build: '{target}' not a valid build target. \n\
                \rValid targets are 'sw_emu' or 'hw_emu' or 'hw'", ex_type='ValueError')

    def generate_build_files(self):
        """
        generate_build_files :
            Generate/regenerate the CMake build files for system project build.
            Edits done outside the tool in CMake files will be lost.

        Prototype:
            status = sys_proj.generate_build_files()

        Arguments:
            None

        Returns:
            True
                Successfully generated files.
            Exception
                Failed to generate files.

        Examples:
            status = sys_proj.generate_build_files()
            status = sys_proj.generate_build_files()

        """
        return (self._buildObj.generateBuildFiles(self.project_name))

    def _listSystemProjects(self):
        try:
            listPrjRequest =  projects_pb2.ListSystemProjectsRequest()
            listPrjResponse = self.stub.ListSystemProjects(listPrjRequest)

            listProjects = list()
            for project in listPrjResponse.system_projects:
                projDict = dict()
                projDict['name'] = project.project_name
                projDict['location'] = project.project_location
                listProjects.append(projDict)

            return listProjects
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot list system projects", ex=e)

    def _getSystemProject(self, name, sec_folder=None):
        try:
            location = self._getProjectLocation(name, "get_sys_project")

            if (location != None):
                getPrjRequest = projects_pb2.GetSystemProjectRequest(project_location=location)
                getPrjResponse = self.stub.GetSystemProject(getPrjRequest)
                self.__assign__(getPrjResponse)

                return self

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot get system project '{name}'", ex=e)

    def _createSystemProject(self, name, platform, template):
        try:
            location = self._getProjectLocation(name, "create_sys_project")

            if (location != None):
                createPrjRequest = projects_pb2.CreateSystemProjectRequest(project_name=name,
                                                                            project_location=location,
                                                                            platform=platform,
                                                                            template=template)
                createPrjResponse = self.stub.CreateSystemProject(createPrjRequest)
                self.__assign__(createPrjResponse)

                return self
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot create system project '{name}'", ex=e)

    def _deleteSystemProject(self, name, sec_folder=None):
        try:
            location = self._getProjectLocation(name, "delete_sys_project")

            if not os.path.exists(location):
                _utils.exception(msg=f"System project '{name}' does not exist.")

            if (location != None):
                delPrjRequest = projects_pb2.DeleteSystemProjectRequest(project_location=location)
                self.stub.DeleteSystemProject(delPrjRequest)
                self = None
                return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot delete system project '{name}'", ex=e)

    def _getProjectLocation(self, name, func, sec_folder=None):
        location = None
        if (sec_folder == None):
            if (self._server.checkWorkspaceSet()):
                workspace = self._server.getWorkspace(func)
                location = workspace + "/" + name
            else:
                _utils.exception(msg=f"{func}: Cannot get project location for '{name}', no workspace is set")
        else:
            location = sec_folder + "/" + name
        return location

    def _setPreference(self, level, device, setting, value):
        if(level.upper() == 'USER'):
            level = projects_pb2.LevelType.USER
        elif(level.upper() == 'WORKSPACE'):
            level = projects_pb2.LevelType.WORKSPACE
        else:
            _utils.exception(msg=f"set_preference: Invalid level type '{level}', \n\
                            \rvalid level types are 'USER', and 'WORKSPACE'")

        if(device.upper() == 'VERSAL'):
            device = projects_pb2.DeviceType.VERSAL
        elif(device.upper() == 'ZYNQ'):
            device = projects_pb2.DeviceType.ZYNQ
        elif(device.upper() == 'ZYNQMP'):
            device = projects_pb2.DeviceType.ZYNQMP
        else:
            _utils.exception(msg=f"set_preference: Invalid device type '{device}', \n\
                            \rvalid device types are 'VERSAL', 'ZYNQ' and 'ZYNQMP'")

        if(setting.upper() == 'SYSROOT'):
            setting = projects_pb2.SettingType.SYSROOT
        elif(setting.upper() == 'KERNELIMAGE'):
            setting = projects_pb2.SettingType.KERNELIMAGE
        elif(setting.upper() == 'ROOTFS'):
            setting = projects_pb2.SettingType.ROOTFS
        else:
            _utils.exception(msg=f"set_preference: Invalid setting type '{device}', \n\
                            \rsupported setting types are 'SYSROOT', 'KERNELIMAGE' and 'ROOTFS'")

        try:
            setpreferencerequest = projects_pb2.SetPreferenceRequest(level = level, device_type = device,
                                                                    setting = setting, value = value)
            response = self.stub.SetPreference(setpreferencerequest)
            return(response)
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot set preference.", ex=e)

    def _getPreference(self, level, device, setting):
        if(level.upper() == 'USER'):
            level = projects_pb2.LevelType.USER
        elif(level.upper() == 'WORKSPACE'):
            level = projects_pb2.LevelType.WORKSPACE
        else:
            _utils.exception(msg=f"get_preference: Invalid level type '{level}', \n\
                            \rvalid level types are 'USER', and 'WORKSPACE'")

        if(device.upper() == 'VERSAL'):
            device = projects_pb2.DeviceType.VERSAL
        elif(device.upper() == 'ZYNQ'):
            device = projects_pb2.DeviceType.ZYNQ
        elif(device.upper() == 'ZYNQMP'):
            device = projects_pb2.DeviceType.ZYNQMP
        else:
            _utils.exception(msg=f"get_preference: Invalid device type '{device}', \n\
                            \rvalid device types are 'VERSAL', 'ZYNQ' and 'ZYNQMP'")

        if(setting.upper() == 'SYSROOT'):
            setting = projects_pb2.SettingType.SYSROOT
        elif(setting.upper() == 'KERNELIMAGE'):
            setting = projects_pb2.SettingType.KERNELIMAGE
        elif(setting.upper() == 'ROOTFS'):
            setting = projects_pb2.SettingType.ROOTFS
        else:
            _utils.exception(msg=f"get_preference: Invalid setting type '{device}', \n\
                            \rsupported setting types are 'SYSROOT', 'KERNELIMAGE' and 'ROOTFS'")

        try:
            getpreferencerequest = projects_pb2.GetPreferenceRequest(level = level, device_type = device,
                                                                     setting = setting)
            response = self.stub.GetPreference(getpreferencerequest)
            return(response)
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot get preference.", ex=e)

    def _cloneSystemProject(self, name, new_name):
        try:
            new_location = self._getProjectLocation(new_name, "clone_sys_project")
            location = self._getProjectLocation(name, "clone_sys_project")

            cloneApplicationRequest = projects_pb2.CloneSystemRequest(app_project_name = new_name,
                                                                      project_location = new_location,
                                                                      source_app_project_location = location)
            project = self.stub.CloneSystem(cloneApplicationRequest)
            clone = Project(self._server)
            clone.__assign__(project)
            return clone

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot clone the project.", ex=e)
