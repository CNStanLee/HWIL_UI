from calendar import c
import grpc
import components_pb2_grpc
import components_pb2
import utils_pb2
import utils_pb2_grpc
import hls_flow_pb2
import hls_flow_pb2_grpc
from vitis import _build
import os
from vitis import _utils
import textwrap
import json
from vitis import _ldfile


class Component(object):
    """
    Client Class for Component service.
    """

    def __init__(self, serverObj):

        self._server = serverObj
        self._buildObj = _build.Build(serverObj)

        self._stub = components_pb2_grpc.ComponentsStub(self._server.channel)
        self._util_stub = utils_pb2_grpc.UtilsServiceStub(self._server.channel)

    #copy grpc object to wrapper object
    def __assign__(self, component):
        self.component_location = component.component_location
        self.component_name = component.component_name
        if(component.component_type == components_pb2.Component.Type.HLS):
            self.component_type = 'HLS'
        elif(component.component_type == components_pb2.Component.Type.AI_ENGINE):
            self.component_type = "AI_ENGINE"
        elif(component.component_type == components_pb2.Component.Type.HOST):
            self.component_type = "APPLICATION"

    def __str__(self) -> str:
        data = f"'component_location': '{self.component_location}'\n"
        data = data + f"'component_name': '{self.component_name}'\n"
        return (data)

    def __repr__(self):
        return (self.__str__())

    def import_files(self, from_loc, files = None, dest_dir_in_cmp = None):
        """
        import_files:
            Import files to the component.

        Prototype:
            status = component.import_files(from_loc = <Location of src or
                                            config file(s) path>,
                                            files = ["file1",..]**,
                                            dest_dir_in_cmp = <Dest location or
                                            config file(s) path>)

        Required Arguments:

            from_loc = <Location of src or config file(s) path>
                From The location can be a directory/file, the path can be
                absolute/relative.

            files = ["file1",..]**
                List of files to be imported from the given from_loc path.

        Returns:
            True
                Files imported successfully.
            Exception
                File could not be imported.

        Examples:
            component.import_files(from_loc = '/tmp/dir1',  
                                   files = ['file1.txt','file2.cpp'], 
                                   dest_dir_in_cmp = 'src')
        """
        if(files is not None and type(files) != list):
            _utils.exception(msg=f"import_files: files = '{files}' is not a valid list. \n\
                \rSpecify files in list format, ex. files = ['src_file1.cpp','config_file1.cfg']")
        try:
            if (self.component_location != None):
                from_loc_abs = os.path.abspath(from_loc)
                dest_loc = self.component_location

                if (dest_dir_in_cmp != None):
                    dest_dir = os.path.join(dest_loc, dest_dir_in_cmp)
                    os.makedirs(dest_dir, exist_ok = True)
                    dest_loc = os.path.abspath(dest_dir)
                
                request = utils_pb2.ImportFilesRequest(src_loc = from_loc_abs,
                                                        dest_loc = dest_loc,
                                                        files = files)
                response = self._util_stub.ImportFiles(request)
                return True

            else:
                _utils.exception(msg=f"import_files: Invalid component")

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="import_files failed", ex=e)

    def remove_files(self, files):
        """
        remove_files:
            Remove files from the component.

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
            component.remove_files(files = ['/src/file1.txt'] )
            component.remove_files(files = ['/src/file1.txt', 'file2.cfg'])
        """
        if(type(files) != list):
            _utils.exception(msg=f"import_files: files = '{files}' is not a valid list. \n\
                \rSpecify files in list format, ex. files = ['src_file1.cpp','config_file1.cfg']")
        try:
            request = utils_pb2.RemoveFilesRequest(src_loc = self.component_location,
                                                   files = files)
            response = self._util_stub.RemoveFiles(request)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="remove_files failed", ex=e)

    def report(self):
        """
        report:
            Print the component information.

        Prototype:
            status = component.report()

        Returns:
            Component information, error in case given component is not
            part of workspace or secondary folders.

        Examples:
            component.report()
        """
        try:
            getComponentRequest = components_pb2.GetComponentRequest(component_location = self.component_location)
            component = self._stub.GetComponent(getComponentRequest)
            if(component!=None):
                print(f"Component Name      :  '{component.component_name}'")
                print(f"Component Location  :  '{component.component_location}'")
                print(f"Component Type      :  '{self.component_type}'")
                if(component.platform != ''):
                    wrapped_path = textwrap.wrap(component.platform+"'", width=60)
                    print(f"Platform            :  '{wrapped_path[0]}")
                    for w in wrapped_path[1:]:
                        print(textwrap.indent(w, '                        ', lambda line: True))
                if(component.part != ''):
                    print(f"Part                :  '{component.part}'")
                if(self.component_type == 'HLS' or self.component_type == 'AI_ENGINE'):
                    if(component.cfg_files):
                        print(f"Cfg file            :  '{component.cfg_files[0]}'")
                if(self.component_type == 'AI_ENGINE'):
                    print(f"Top level file      :  '{component.aie_graph_top_file}'")
                if(self.component_type == 'APPLICATION'):
                    print(f"Domain              :  '{component.domain}'")
                    print(f"CPU instance        :  '{component.cpu_instance}'")
                    if(component.sysroot):
                        wrapped_path = textwrap.wrap(component.sysroot+"'", width=60)
                        print(f"Sysroot             :  '{wrapped_path[0]}")
                        for w in wrapped_path[1:]:
                            print(textwrap.indent(w, '                        ', lambda line: True))
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="report component failed", ex=e)


    @classmethod
    def _listComponents(self, channel):
        try:
            listComponentRequest = components_pb2.ListComponentsRequest()
            componentStub = components_pb2_grpc.ComponentsStub(channel)
            response = componentStub.ListComponents(listComponentRequest)
            return response

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="list_components failed", ex=e)

    def _getComponentLocation(self, name, func):
        location = None
        if (self._server.checkWorkspaceSet()):
            workspace = self._server.getWorkspace(func)
            location = workspace + "/" + name
        else:
            _utils.exception(msg=f"{func}: Cannot get component location for '{name}', no workspace is set")
        return location

    @classmethod
    def _deleteComponent(self, channel, name):
        try:
            
            componentStub = components_pb2_grpc.ComponentsStub(channel)
            deleteComponentRequest = components_pb2.DeleteComponentRequest(component_location = name)
            status = componentStub.DeleteComponent(deleteComponentRequest)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot delete the component", ex=e)

    @classmethod
    def _getComponent(self, channel, name):
        try:
            getComponentRequest = components_pb2.GetComponentRequest(component_location = name)
            componentStub = components_pb2_grpc.ComponentsStub(channel)
            component = componentStub.GetComponent(getComponentRequest)
            return component

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot get the component.", ex=e)

    @classmethod
    def _cloneComponent(self, serverObj, name, new_name):
        try:
            # new_location = self._getComponentLocation(new_name, "clone_component")
            # location = self._getComponentLocation(name, "clone_component")
            location = None
            new_location = None
            if (serverObj.checkWorkspaceSet()):
                workspace = serverObj.getWorkspace('clone_component')
                location = workspace + "/" + name
                new_location = workspace + "/" + new_name

            cloneComponentRequest = components_pb2.CloneComponentRequest(component_name = new_name,
                                                                         component_location = new_location,
                                                                         source_component_location = location)
            componentStub = components_pb2_grpc.ComponentsStub(serverObj.channel)
            component = componentStub.CloneComponent(cloneComponentRequest)
            return component

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot clone the component.", ex=e)


class HLSComponent(Component):
    """
    Client Class for HLS Component service.
    """

    def __init__(self, serverObj):
        super().__init__(serverObj)
        self._hls_flow_stub = hls_flow_pb2_grpc.HLSFlowStub(self._server.channel)

    #copy grpc object to wrapper object
    def __assign__(self, component):
        super().__assign__(component)
        self.component_location = component.component_location
        self.component_name = component.component_name

    def _createHLSComponent(self, name, cfg_file, template):
        try:
            # Converting single cfg file into list. Remove this if cfg file becomes single file in the backend
            if(cfg_file!=None):
                if(type(cfg_file)!=list):
                    cfg_file = [cfg_file]
            else:
                cfg_file = []
            
            location = self._getComponentLocation(name, "create_hls_component")
            createComponentRequest = components_pb2.CreateComponentRequest(component_name = name,
                                                                           component_location = location,
                                                                           component_type = components_pb2.Component.Type.HLS,
                                                                           cfg_files = cfg_file,
                                                                           template = template)
            component = self._stub.CreateComponent(createComponentRequest)
            self.__assign__(component)
            return self

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot create component", ex=e)

    def _getHLSComponent(self, component):
        self.__assign__(component)
        return self

    def add_cfg_file(self, cfg_file):
        """
        add_cfg_file:
            Add configuration file to the component.

        Prototype:
            status = component.add_cfg_file(cfg_file = <file>)

        Required Arguments:

            cfg_file = <file>
                Configuration file to be associated with the component.

        Returns:
            True
                File added successfully.
            Exception
                File could not be added.

        Examples:
            component.add_cfg_file(file = '/tmp/hls_config.cfg')
        """
        if(type(cfg_file) == str):
            cfg_file = [cfg_file]

        else:
            _utils.exception(msg=f"add_cfg_files: cfg_file = '{cfg_file}' is not a valid path. \n\
            \rSpecify cfg_file in string format.")

        try:
            addCfgFileRequest = components_pb2.AddCfgFilesRequest(component_location = self.component_location, files = cfg_file, save = True)
            component = self._stub.AddCfgFiles(addCfgFileRequest)
            self.__assign__(component)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="add_cfg_files failed", ex=e)

    def remove_cfg_file(self, cfg_file):
        """
        remove_cfg_file:
            Remove configuration file from the component.
            
        NOTE: Cfg file path should be exact path used while adding.
              To get the exact cfg path, use component.report().
              For removing default cfg use "hls_config.cfg".

        Prototype:
            status = component.remove_cfg_file(cfg_file = <file>)

        Required Arguments:

            cfg_file = <file>
                Configuration file to be removed from the component.

        Returns:
            True
                Files added successfully.
            Exception
                File could not be added.

        Examples:
            component.remove_cfg_file('hls_config.cfg')
                Removes the default cfg file created in the component.
            component.remove_cfg_file('/tmp/custom_config.cfg')
        """
        if(type(cfg_file) == str):
            cfg_file = [cfg_file]           

        else:
            _utils.exception(msg=f"remove_cfg_file: cfg_file = '{cfg_file}' is not a valid path. \n\
            \rSpecify cfg_file in string format.")

        try:
            if (len(cfg_file) > 0):
                removeCfgFileRequest = components_pb2.RemoveCfgFilesRequest(component_location = self.component_location, files = cfg_file, save = True)
                component = self._stub.RemoveCfgFiles(removeCfgFileRequest)
                self.__assign__(component)

            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot remove cfg file.", ex=e)

    # Following functions are to be  used when multiple cfg files are supported in hls and aie component
    
    # def add_cfg_files(self, cfg_files):
    #     """
    #     add_cfg_file:
    #         Add configuration files to the component.

    #     Prototype:
    #         status = component.add_cfg_file(cfg_files = ["file1",..]**)

    #     Required Arguments:

    #         cfg_files = ["file1",..]**
    #             Configuration files to be associated with the component.

    #     Returns:
    #         True
    #             Files added successfully.
    #         Exception
    #             File could not be added.

    #     Examples:
    #         component.add_cfg_file(files = ["file1", "file2"])
    #     """
    #     if(type(cfg_files) != list):
    #         _utils.exception(msg=f"add_cfg_files: cfg_files = '{cfg_files}' is not a valid list. \n\
    #             \rSpecify cfg_files in list format, ex. cfg_files = ['config_file1.cfg','config_file1.cfg']")
    #     try:
    #         if (len(cfg_files) > 0):
    #             addCfgFileRequest = components_pb2.AddCfgFilesRequest(component_location = self.component_location, files = cfg_files, save = True)
    #             component = self._stub.AddCfgFiles(addCfgFileRequest)
    #             print(component.cfg_files)
    #             self.__assign__(component)
    #             return True

    #         else :
    #             _utils.exception(msg="add_cfg_files: config file list is empty")

    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg="add_cfg_files failed", ex=e)

    # def remove_cfg_files(self, cfg_files):
    #     """
    #     remove_cfg_file:
    #         Remove configuration files from the component.

    #     Prototype:
    #         status = component.remove_cfg_file(cfg_files = ["file1",..]**)

    #     Required Arguments:

    #         cfg_files = ["file1",..]**
    #             Configuration files to be removed from the component.

    #     Returns:
    #         True
    #             Files added successfully.
    #         Exception
    #             File could not be added.

    #     Examples:
    #         component.remove_cfg_file()
    #     """
    #     if(type(cfg_files) != list):
    #         _utils.exception(msg=f"remove_cfg_files: cfg_files = '{cfg_files}' is not a valid list. \n\
    #             \rSpecify cfg_files in list format, ex. cfg_files = ['config_file1.cfg','config_file1.cfg']")
    #     try:
    #         if (len(cfg_files) > 0):
    #             removeCfgFileRequest = components_pb2.RemoveCfgFilesRequest(component_location = self.component_location, files = cfg_files, save = True)
    #             component = self._stub.RemoveCfgFiles(removeCfgFileRequest)
    #             self.__assign__(component)

    #         return True

    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg=f"Cannot remove cfg files", ex=e)


    def execute(self, operation):
        """
        execute:
            Run a specified operation on the HLS component.

        Prototype:
            status = component.execute(operation = <operation_type>)

        Required Arguments:
            operation = <operation_type>
                Operation to be executed. Valid types are 'C_SIMULATION', 
                'SYNTHESIS', 'CO_SIMULATION', 'IMPLEMENTATION', 
                'ANALYSIS_OPTIMIZATION', and 'PACKAGE'

        Returns:
            True
                Successfully executed the action on the component.
            Exception
                Failed to execute the action.

        Examples:
            status = comp1.execute(operation = 'SYNTHESIS')
        """
        try:
            if(operation == 'C_SIMULATION'):
                operation_type = hls_flow_pb2.OperationType.C_SIMULATION
            elif(operation == 'SYNTHESIS'):
                operation_type = hls_flow_pb2.OperationType.SYNTHESIS
            elif(operation == 'CO_SIMULATION'):
                operation_type = hls_flow_pb2.OperationType.CO_SIMULATION
            elif(operation == 'IMPLEMENTATION'):
                operation_type = hls_flow_pb2.OperationType.IMPLEMENTATION
            elif(operation == 'ANALYSIS_OPTIMIZATION'):
                operation_type = hls_flow_pb2.OperationType.ANALYSIS_OPTIMIZATION
            elif(operation == 'PACKAGE'):
                operation_type = hls_flow_pb2.OperationType.PACKAGE
            else:
                _utils.exception(msg=f"Invalid operation type '{operation}'")
            
            request = hls_flow_pb2.OperationRequest(component_location = self.component_location, operation_type = operation_type)
            
            response = self._hls_flow_stub.runOperation(request)

            retStatus = None
            for buildStream in response:
                retStatus = buildStream.status
                for logLine in buildStream.log:
                    print(logLine)

                if(retStatus == hls_flow_pb2.StatusType.SUCCESS):
                    return ('')
                elif(retStatus == hls_flow_pb2.StatusType.FAILURE):
                    _utils.exception(msg=f"Could not execute the operation.")

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Could not execute the operation.", ex=e)


class AIEComponent(Component):
    """
    Client Class for AIE Component service.
    """

    def __init__(self, serverObj):
        super().__init__(serverObj)

    #copy grpc object to wrapper object
    def __assign__(self, component):
        super().__assign__(component)
        self.component_location = component.component_location
        self.component_name = component.component_name

    def _createAIEComponent(self, name, platform, part, template):
        try:
            location = self._getComponentLocation(name, "create_aie_component")
            createComponentRequest = components_pb2.CreateComponentRequest(component_name = name,
                                                                            component_location = location,
                                                                            component_type = components_pb2.Component.Type.AI_ENGINE,
                                                                            platform = platform,
                                                                            part = part,
                                                                            template = template)
            component = self._stub.CreateComponent(createComponentRequest)
            self.__assign__(component)
            return self

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot create AIE component", ex=e)

    def _getAIEComponent(self, component):
        self.__assign__(component)
        return self

    def add_cfg_file(self, cfg_file):
        """
        add_cfg_file:
            Add configuration file to the component.

        Prototype:
            status = component.add_cfg_file(cfg_file = <file>)

        Required Arguments:

            cfg_file = <file>
                Configuration file to be associated with the component.

        Returns:
            True
                File added successfully.
            Exception
                File could not be added.

        Examples:
            component.add_cfg_file(file = '/tmp/aie_config.cfg')
        """
        if(type(cfg_file) == str):
            cfg_file = [cfg_file]
        else:
            _utils.exception(msg=f"add_cfg_files: cfg_file = '{cfg_file}' is not a valid path. \n\
            \rSpecify cfg_file in string format.")

        try:
            addCfgFileRequest = components_pb2.AddCfgFilesRequest(component_location = self.component_location, files = cfg_file, save = True)
            component = self._stub.AddCfgFiles(addCfgFileRequest)
            self.__assign__(component)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="add_cfg_files failed", ex=e)

    def remove_cfg_file(self, cfg_file):
        """
        remove_cfg_file:
            Remove configuration file from the component.
            
        NOTE: Cfg file path should be exact path used while adding.
            To get the exact cfg path, use component.report().

        Prototype:
            status = component.remove_cfg_file(cfg_file = <file>)

        Required Arguments:

            cfg_file = <file>
                Configuration file to be removed from the component.

        Returns:
            True
                Files added successfully.
            Exception
                File could not be added.

        Examples:
            component.remove_cfg_file('/tmp/aie_cfg.cfg')
        """
        if(type(cfg_file) == str):
            cfg_file = [cfg_file]    

        else:
            _utils.exception(msg=f"remove_cfg_file: cfg_file = '{cfg_file}' is not a valid path. \n\
            \rSpecify cfg_file in string format.")

        try:
            if (len(cfg_file) > 0):
                removeCfgFileRequest = components_pb2.RemoveCfgFilesRequest(component_location = self.component_location, files = cfg_file, save = True)
                component = self._stub.RemoveCfgFiles(removeCfgFileRequest)
                self.__assign__(component)

            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot remove cfg file.", ex=e)

    def update_top_level_file(self, top_level_file):
        """
        update_top_level_file:
            Update the top level file of aie component.

        Prototype:
            status = component.update_top_level_file(top_level_file = <file>)

        Required Arguments:

            top_level_file = <file>
                Top level file to be associated with specified aie component.

        Returns:
            True
                Top level file updated successfully.
            Exception
                Top level file could not be updated.

        Examples:
            status = component.update_top_level_file('graph1.cpp')
        """
        try:
            updateCompRequest = components_pb2.UpdateAieGraphFileRequest(component_location = self.component_location, graph_file = top_level_file, save = True)
            component = self._stub.UpdateAieGraphFile(updateCompRequest)
            self.__assign__(component)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot update top level file", ex=e)

    def clean(self, target = None):
        """
        clean:
            Clean the given component for the specified build target.

        Prototype:
            status = component.clean(target = <target_name>)

        Required Arguments:
            target = <target name> - One of the supported targets
                                     (sw_emu/hw_emu/hw).

        Returns:
            Build Status
                SUCCESS/FAILURE
            Exception
                Failed to clean the component.

        Examples:
            status = component.clean(target = "hw")
        """

        if(target == None):
            target = "x86sim"
        if (target == "x86sim" or target == "hw"):
            return (self._buildObj.clean_comp(self.component_name,components_pb2.Component.Type.AI_ENGINE,target))
        else:
            _utils.exception(msg=f"clean: '{target}' not a valid target. \n\
                \rValid targets are 'x86sim' or 'hw'", ex_type='ValueError')

    def build(self, target = None):
        """
        build:
            Initiates the build of a component.

        Prototype:
            status = component.build(target= <target name>)

        Optional arguments:
            target = <target name>
                One of the supported targets - x86sim,hw
                x86sim (Default)

        Returns:
            Build Status
                SUCCESS/FAILURE
            Exception
                Failed to build the component.

        Examples:
            status = component.build(target = "hw")
        """

        if(target == None):
            target = "x86sim"
        if (target == "x86sim" or target == "hw"):
            return (self._buildObj.build_comp(self.component_name,components_pb2.Component.Type.AI_ENGINE,target))
        else:
            _utils.exception(msg=f"build: '{target}' not a valid build target. \n\
                \rValid targets are 'x86sim' or 'hw'", ex_type='ValueError')

    def generate_build_files(self):
        """
        generate_build_files :
            Generate/regenerate the CMake build files for component build.
            Edits done outside the tool in CMake files will be lost.

        Prototype:
            status = component.generate_build_files()

        Arguments:
            None

        Returns:
            True
                Successfully generated files.
            Exception
                Failed to generate files.

        Examples:
            status = component.generate_build_files()
            status = component.generate_build_files()

        """
        return (self._buildObj.generateBuildFiles(self.component_name))

class HostComponent(Component):
    """
    Client Class for Application Component service.
    """

    def __init__(self, serverObj):
        super().__init__(serverObj)

    #copy grpc object to wrapper object
    def __assign__(self, component):
        super().__assign__(component)
        self.component_location = component.component_location
        self.component_name = component.component_name

    def _createHostComponent(self, name, platform, domain, template):
        location = self._getComponentLocation(name, "create_app_component")
        try:
            createComponentRequest = components_pb2.CreateComponentRequest(component_name = name,
                                                                           component_location = location,
                                                                           component_type = components_pb2.Component.Type.HOST,
                                                                           platform = platform,
                                                                           domain = domain,
                                                                           template = template)
            component = self._stub.CreateComponent(createComponentRequest)
            self.__assign__(component)
            return self

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot create application component", ex=e)

    def _getHostComponent(self, component):
        self.__assign__(component)
        return self

    def set_sysroot(self, sysroot):
        """
        set_sysroot:
            Set sysroot for the app component.

        Prototype:
            app_component.set_sysroot(sysroot = <sysroot>)

        Required Arguments:
            sysroot = <sysroot>

        Returns:
            True
                Sysroot set successfully.
            False
                Failed to set sysroot.

        Examples:
            app_comp.set_sysroot(sysroot = 'my_sysroots/cortexa53-xilinx-linux')
        """
        try:
            setsysrootrequest = components_pb2.SetSysRootRequest(project_location = self.component_location,
                                                           sysroot = sysroot, save=True)
            response = self._stub.SetSysRoot(setsysrootrequest)
            return(response)
        
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Couldn't set the sysroot.", ex=e)

    def get_sysroot(self):
        """
        Waiting for backend support

        get_sysroot:
            Get sysroot for the the app component.

        Prototype:
            sysroot = app_component.get_sysroot()

        Arguments:
            None

        Returns:
            Sysroot location associated with the app component.

        Examples:
            sysroot = app_comp.get_Sysroot()
        """
        try:
            getsysrootrequest = components_pb2.GetSysRootRequest(project_location = self.component_location)
            response = self._stub.GetSysRoot(getsysrootrequest)
            return(response)
        
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Couldn't get the sysroot.", ex=e)

    def clean(self, target = None):
        """
        clean:
            Clean the given component for the specified build target.

        Prototype:
            status = component.clean(target = <target_name>)

        Required Arguments:
            target = <target name> - One of the supported targets
                                     (sw_emu/hw_emu/hw).

        Returns:
            Build Status
                SUCCESS/FAILURE
            Exception
                Failed to clean the component.

        Examples:
            status = component.clean(target = "hw")
        """

        if (target == None or target == "x86sim" or target == "hw"):
            return (self._buildObj.clean_comp(self.component_name,components_pb2.Component.Type.HOST,target))
        else:
            _utils.exception(msg=f"clean: '{target}' not a valid build target. \n\
                \rValid targets are 'x86sim' or 'hw'", ex_type='ValueError')
            
    # APIs for the C/C++ build settings
    
    def get_app_config(self, key = None):
        """
        get_app_config:
            Get the current build configuration for the provided setting.
            In case of no setting is provided, build configuration of the
            application component is returned.

        Prototype:
            value = component.get_app_config(key = <setting>)

        Optional arguments:
            key = <setting>
                Configuration parameter.
                Current build configuration for the application is returned 
                if no key is provided.(default)

        Returns:
            Configuration value(s).

        Examples:
            value = component.get_app_config(key = 
                                           "USER_COMPILE_OPTIMIZATION_LEVEL")
        """
        config = self._buildObj.getAppConfig(self.component_location)
        my_dict = {}
        my_dict['key'] = 'value(s)'
        if(config!=None):
            for setting in config.settings:
                if(key!=None and key.upper()==setting.key):
                    return setting.value
                my_dict[setting.key] = ','.join(setting.value)
        
        if(key!=None):
            _utils.exception(msg=f"get_app_config: '{key}' is not a valid key.")
        self._print_dict_table(my_dict)
    
    def set_app_config(self, key, values):
        """
        set_app_config:
            Set the value of the provided build setting.
            Values can be single value or a list of values.

        Prototype:
            status = component.set_app_config(key = <setting>, 
                                             value = ["value1",..]**)

        Required arguments:
            key = <setting>
                Configuration parameter to be set.
            values = ["value1",..]**
                New value(s) for the configuration parameter.

        Returns:
            True
                Build configuration set successfully.
            Exception
                Failed to set the configuration.

        Examples:
            status = component.set_app_config(
                                        key = "USER_COMPILE_DEBUG_LEVEL",
                                        values = "-g1")
        """
        if(type(values) == str):
            values = [values]
        data = self.get_config_info(key)
        if(data['multiple_values_possible'] == 'False' and len(values)>1):
            _utils.exception(msg=f"append_app_config: Multiple values are not allowed for this setting.")
        self._buildObj.setAppConfig(self.component_location, key, values)
        return True
        
    def append_app_config(self, key, values):
        """
        append_app_config:
            Append the value to the provided build setting. Append option is
            only supported for 'USER_COMPILE_DEFINITIONS','USER_LINK_LIBRARIES'
            ,'USER_UNDEFINE_SYMBOLS','USER_INCLUDE_DIRECTORIES'.

        Prototype:
            status = component.append_app_config(key = <setting>, 
                                                 values = ["value1",..]**)

        Required arguments:
            key = <setting>
                Configuration parameter to be updated.
            value = <value>
                New value(s) to be appended in the configuration parameter 
                value.

        Returns:
            True
                Build configuration updated successfully.
            Exception
                Failed to update the configuration.

        Examples:
            status = component.append_app_config(
                                    key = "USER_INCLUDE_DIRECTORIES",
                                    values = ["/tmp/test1", "/tmp/test2"])
        """
        if(type(values) == str):
            values = [values]
        data = self.get_config_info(key)
        if(data['multiple_values_possible'] == 'False'):
            _utils.exception(msg=f"append_app_config: Multiple values are not allowed for this setting.")

        old_value = self.get_app_config(key)
        old_value.extend(values)
        self.set_app_config(key, old_value)
        return(True)
        
    def remove_app_config(self, key, values):
        """
        remove_app_config:
            Remove the value from the provided build setting. Remove option is
            only supported for 'USER_COMPILE_DEFINITIONS','USER_LINK_LIBRARIES'
            ,'USER_UNDEFINE_SYMBOLS','USER_INCLUDE_DIRECTORIES'.

        Prototype:
            status = component.remove_app_config(key = <setting>, 
                                                 values = ["value1",..]**)

        Required arguments:
            key = <setting>
                Configuration parameter to be updated.
            value = ["value1",..]**
                Value(s) to be removed from the configuration parameter value.

        Returns:
            True
                Build configuration updated successfully.
            Exception
                Failed to update the configuration.l

        Examples:
            status = component.remove_app_config(
                                        key = "USER_INCLUDE_DIRECTORIES",
                                        values = "/tmp/test1")
        """
        if(type(values) == str):
            values = [values]
            
        data = self.get_config_info(key)
        if(data['multiple_values_possible'] == 'False'):
            _utils.exception(msg=f"append_app_config: Append/remove are not allowed for this setting.")
        
        old_value = set(self.get_app_config(key))
        values = set(values)
        new_values = list(old_value - values)
        self.set_app_config(key, new_values)
        return(True)
        
    def get_config_info(self, key):
        """
        get_config_info:
            Display more information like possible values and possible 
            operations about the configuration parameter.

        Prototype:
            status = component.get_config_info(key = <setting>)

        Required arguments:
            key = <setting>
                Configuration parameter.

        Returns:
            Configuration parameter information.

        Examples:
            status = component.get_config_info(key = 
                                             "USER_COMPILE_OPTIMIZATION_LEVEL")
        """
        try:
            xilinxVitisEnv = os.getenv("XILINX_VITIS")
            if (xilinxVitisEnv != None) :
                cmake_json = xilinxVitisEnv + "/vitisng-server/scripts/cmake/user_cmake.json"
            f = open(cmake_json)
            json_data = json.load(f)
            if(key in json_data.keys()):
                data = json_data[key]
                return data
            else:
                _utils.exception(msg=f"get_config_info: Invalid key '{key}'")
        except:
            _utils.exception(msg=f"get_config_info: Unable to get the config information'")
        finally:
            f.close()

    def build(self, target = None):
        """
        build:
            Initiates the build of a component.

        Prototype:
            status = component.build(target= <target name>)

        Optional arguments:
            target = <target name>
                One of the supported targets - x86sim,hw
                x86sim (Default)

        Returns:
            Build Status
                SUCCESS/FAILURE
            Exception
                Failed to build the component.

        Examples:
            status = component.build(target = "hw")
        """

        if (target == None or target == "x86sim" or target == "hw"):
            return (self._buildObj.build_comp(self.component_name,components_pb2.Component.Type.HOST,target))
        else:
            _utils.exception(msg=f"build: '{target}' not a valid build target. \n\
                \rValid targets are 'None' or 'x86sim' or 'hw'", ex_type='ValueError')

    def generate_build_files(self):
        """
        generate_build_files :
            Generate/regenerate the CMake build files for component build.
            Edits done outside the tool in CMake files will be lost.

        Prototype:
            status = component.generate_build_files()

        Arguments:
            None

        Returns:
            True
                Successfully generated files.
            Exception
                Failed to generate files.

        Examples:
            status = component.generate_build_files()
            status = component.generate_build_files()

        """
        return (self._buildObj.generateBuildFiles(self.component_name))
    
    # Method to format the build settings
    def _print_dict_table(self,dictionary):
        
        max_key_length = max(len(str(key)) for key in dictionary.keys())
        max_value_length = max(len(str(value)) for value in dictionary.values())
        
        print(f'{"Key":<{max_key_length}} | {"Value":<{max_value_length}}')
        print('-' * (max_key_length + max_value_length + 3))
        
        for key, value in dictionary.items():
            print(f'{str(key):<{max_key_length}} | {str(value):<{max_value_length}}')
            
    # Get oject for linker script
    def get_ld_script(self, path = None):
        """
        get_ld_script:
            Get the linker script object corresponding to the host_component.

        Prototype:
            status = ldfile.get_ld_script(path = <ld_path>)

        Optional Arguments:
            path = <ld_path>
                Linker script path to be edited.
                lscript.ld associated with the host component will be 
                considered by default.

        Returns:
            Linker script file object.

        Examples:
            status = ldfile.get_ld_script()
        """
        try:
            if(path == None):
                ld_path = ''
                src_dir = os.path.join(self.component_location, 'src')
                for file in os.listdir(src_dir):
                    if file.endswith(".ld"):
                        ld_path = os.path.join(src_dir, file)
                if(ld_path == ''):
                    _utils.exception(msg=f"get_ld_script: Unable to locate the linker script in the appliation component.")
            else:
                ld_path = path
            
            _ldObj = _ldfile.Ldfile(self._server)
            _ldObj.__assign__(ld_path)
            return _ldObj

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_ld_script failed", ex=e)
