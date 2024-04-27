from ntpath import abspath
import grpc
import components_pb2_grpc
import components_pb2
import platform_pb2_grpc
import platform_pb2
from vitis import _domain
from vitis import _utils
import textwrap
import os


class Platform(object):
    """
    Client Class for Vitis Project service.
    """

    def __init__(self, server):

        self._server = server
        # self._domainObj = _domain.Domain(server)
        self._stub = platform_pb2_grpc.PlatformStub(self._server.channel)
        self._component_stub = components_pb2_grpc.ComponentsStub(self._server.channel)

    def __assign__(self, platform_proj):
        self.project_name = platform_proj.platform_name
        self.project_location = platform_proj.platform_location

    def __component_assign__(self, component):
        self.project_name = component.component_name
        self.project_location = component.component_location

    def __str__(self) -> str:
        data = f"'project_name': {self.project_name}\n"
        data = data + f"'project_location': '{self.project_location}'\n"
        return (data)

    def __repr__(self):
        return (self.__str__())

    def build(self):
        """
        build:
            Generate the platform.

        Prototype:
            status = platform.build()

        Arguments:
            None

        Returns:
            True
                Platform built successfully.
            Exception
                Platform could not be built.

        Examples:
            platform.built()
        """
        try:
            generateBuildReq = platform_pb2.GeneratePlatformRequest(platform_location = self.project_location)
            buildResponse = self._stub.GeneratePlatform(generateBuildReq)
            retStatus = None
            for buildStream in buildResponse:
                retStatus = buildStream.type
                for logLine in buildStream.log:
                     print(logLine)

            return retStatus
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="platform build failed", ex=e)

    def clean(self):
        """
        clean:
            Clean the given platform.

        Prototype:
            status = platform.clean()

        Arguments:
            None

        Returns:
            Build Status
                SUCCESS/FAILURE
            Exception
                Failed to clean the component.

        Examples:
            status = platform.clean()
        """
        try:
            cleanReq = platform_pb2.CleanPlatformRequest(platform_location = self.project_location)
            cleanResponse = self._stub.CleanPlatform(cleanReq)
            retStatus = None
            for cleanStream in cleanResponse:
                retStatus = cleanStream.type
                for logLine in cleanStream.log:
                     print(logLine)

            return retStatus
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="platform build failed", ex=e)

    def report(self):
        """
        report:
            Display information of the platform.

        Prototype:
            platform.report()

        Arguments:
            None

        Returns:
            Prints information about the platform.

        Examples:
            platform.report()
        """
        try:
            getPlatformRequest = platform_pb2.GetPlatformRequest(platform_location = self.project_location)
            platform = self._stub.GetPlatform(getPlatformRequest)
            print("\nPlatform details:\n")
            if (platform != None):
                    print(f"Platform Name       :  '{platform.platform_name}'")
                    print(f"Project Location    :  '{platform.platform_location}'")

                    if(platform.xsa_path!=''):
                        wrapped_path = textwrap.wrap(platform.xsa_path+"'", width=56)
                        print(f"XSA Path            :  '{wrapped_path[0]}")
                        for w in wrapped_path[1:]:
                            print(textwrap.indent(w, '                        '))

                    if(platform.emulation_xsa_path!=''):
                        wrapped_desc = textwrap.wrap(platform.emulation_xsa_path +"'", width=56)
                        print(f"Description         :  '{wrapped_desc[0]}")
                        for w in wrapped_desc[1:]:
                            print(textwrap.indent(w, '                        '))

                    if(platform.emulation_xsa_Path_in_Platform!=''):
                        wrapped_desc = textwrap.wrap(platform.emulation_xsa_Path_in_Platform +"'", width=56)
                        print(f"Description         :  '{wrapped_desc[0]}")
                        for w in wrapped_desc[1:]:
                            print(textwrap.indent(w, '                        '))

                    wrapped_desc = textwrap.wrap(platform.platform_description +"'", width=56)
                    print(f"Description         :  '{wrapped_desc[0]}")
                    for w in wrapped_desc[1:]:
                        print(textwrap.indent(w, '                        '))

                    print(f"Domains:")
                    listDomainRequest = platform_pb2.ListDomainRequest(platform_location = self.project_location)
                    domains = self._stub.ListDomains(listDomainRequest)
                    for d in domains.domain:
                        print(f"                    :  '{d.name}'")

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot get platform", ex=e)


    def add_domain(self, cpu, os = 'standalone', name = None, display_name = None, sd_dir = None, support_app = None):
        """
        add_domain:
            Add the domain to the platform

        Prototype:
            status = platform.add_domain(cpu = <cpu_core>,
                                         os = <os>
                                         name = <domain_name>,
                                         display_name = <display_name>,
                                         support_app = <app_name>,
                                         sd_dir = <location>)

        Required Arguments:
            name = <domain_name>
                Name of the domain to be added.
            cpu = <cpu_core>
                Processor core to be used for creating the domain. For SMP
                Linux, this can be a list of processor cores.

        Optional Arguments:
            os = <os>
                OS type. OS is standalone (default).
            display_name = <display_name>
                Display name for the domain.
            support_app = <app_name>
                Create a domain with BSP settings needed for application
                specified. This option is valid only for standalone domains.
            sd_dir = <location>
                For domain with Linux as OS, use pre-built Linux images from
                this directory, while creating the PetaLinux project. This
                option is valid only for Linux domains.

        Returns:
            True
                Domain added successfully.
            Exception
                Domain could not be added.

        Examples:
            platform.add_domain(cpu = "psu_cortexa53_0", os = "standalone",
                                 name = "a53_standalone")
        """
        try:
            addDomainRequest = platform_pb2.AddDomainRequest(platform_location = self.project_location, name = name, display_name = display_name, processor = cpu, os = os, sdcard_directory = sd_dir, template = support_app)
            response = self._stub.AddDomain(addDomainRequest)
            _domainObj = _domain.Domain(self._server)
            _domainObj.__assign__(response)
            return(_domainObj)

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="add_domain failed", ex=e)

    def list_domains(self):
        """
        list_domains:
            List all the domains in the platform.

        Prototype:
            status = platform.list_domains()

        Arguments:
            None

        Returns:
            List of all the domains in the platform.

        Examples:
            platform.list_domains()
        """
        try:
            listDomainRequest = platform_pb2.ListDomainRequest(platform_location = self.project_location)
            domains = self._stub.ListDomains(listDomainRequest)
            i=1
            print("\nList of domains:")
            domainsList = list()
            for d in domains.domain:
                dom = dict()
                print("\nDomain ",i,":")
                i = i+1
                print(f"Domain name         :  '{d.name}'")
                print(f"Display name        :  '{d.display_name}'")
                print(f"Processor           :  '{d.processor}'")
                print(f"OS                  :  '{d.os}'")
                dom['domain_name'] = d.name
                dom['display_name'] = d.display_name
                dom['processor'] = d.processor
                dom['os'] = d.os
                domainsList.append(dom)
            return domainsList
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="list_domains failed", ex=e)

    def get_domain(self, name):
        """
        get_domain:
            Get the domain object from the platform.

        Prototype:
            status = platform.get_domain(name = <domain_name>)

        Required Arguments:

            name = <domain_name>
                Name of the domain.

        Returns:
            Domain object.

        Examples:
            platform.get_domain(name = "domain1")
        """
        try:
            getDomainRequest = platform_pb2.GetDomainRequest(platform_location = self.project_location, name = name)
            response = self._stub.GetDomain(getDomainRequest)
            _domainObj = _domain.Domain(self._server)
            _domainObj.__assign__(response)
            return(_domainObj)

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_domain failed", ex=e)

    def delete_domain(self, name):
        """
        delete_domain:
            Delete the domain from the platform.

        Prototype:
            status = platform.delete_domain(name = <domain_name>)

        Required Arguments:

            name = <domain_name>
                Name of the domain to be deleted.

        Returns:
            True
                Domain deleted successfully.
            Exception
                Domain could not be deleted.

        Examples:
            platform.delete_domain(name = "domain1")
        """
        try:
            deleteDomainRequest = platform_pb2.DeleteDomainRequest(platform_location = self.project_location, name = name)
            response = self._stub.DeleteDomain(deleteDomainRequest)
            return(True)
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_domain failed", ex=e)

    # Platform config APIs

    def update_desc(self, desc):
        """
        update_desc:
            Update the description of the platform.

        Prototype:
            status = platform.update_desc(desc = <description>)

        Required Arguments:
            desc = <description>
                Description of the platform.

        Returns:
            True
                Description updated successfully.
            Exception
                Description could not be updated.

        Examples:
            platform.update_desc("Memory test application for Zynq")
        """
        try:
            updatePlatformComponentRequest = platform_pb2.UpdatePlatformComponentRequest(platform_location = self.project_location, platform_name = self.project_name, description = desc, target_processor = None)
            response = self._stub.UpdatePlatformComponent(updatePlatformComponentRequest)
            return(True)
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="update_desc failed", ex=e)

    def generate_boot_bsp(self, target_processor = None):
        """
        generate_boot_bsp:
            Generate boot components for the platform.

        Prototype:
            status = platform.generate_boot_bsp()

        Optional Arguments:
            target_processor = <processor>
                Target procesor for generating boot bsp.
                zynqmp_fsbl (default)

        Returns:
            True
                Boot components generated successfully.
            Exception
                Boot components could not be generated.

        Examples:
            platform.generate_boot_bsp()
        """
        try:
            updatePlatformComponentRequest = platform_pb2.UpdatePlatformComponentRequest(platform_location = self.project_location, platform_name = self.project_name, is_custom_fsbl = False, target_processor = target_processor)
            self._stub.UpdatePlatformComponent(updatePlatformComponentRequest)
            return(True)
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="generate_boot_bsp failed", ex=e)

    def remove_boot_bsp(self, fsbl_path = None, pmufw_elf = None):
        """
        remove_boot_bsp:
            Remove all the boot components generated during platform creation.

        Prototype:
            status = platform.remove_boot_bsp()

        Arguments:
            None

        Returns:
            True
                Boot components removed successfully.
            Exception
                Could not remove boot components.

        Examples:
            platform.remove_boot_bsp()
        """
        try:
            updatePlatformComponentRequest = platform_pb2.UpdatePlatformComponentRequest(platform_location = self.project_location, platform_name = self.project_name, is_custom_fsbl = True, target_processor = None)
            self._stub.UpdatePlatformComponent(updatePlatformComponentRequest)
            return(True)
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="remove_boot_bsp failed", ex=e)
            
    def set_fsbl_elf(self, path):
        """
        set_fsbl_elf:
            Set the prebuilt fsbl elf to be used as boot component when boot
            components are removed.

        Prototype:
            status = platform.set_fsbl_elf(path = <path>)

        Optional Arguments:
            path = <path>
                Prebuilt fsbl.elf path.

        Returns:
            True
                FSBL elf added successfully.
            Exception
                Could not add FSBL elf.
                
        Examples:
            platform.set_fsbl_elf('/tmp/my_fsbl_files/custom_fsbl.elf')
        """
        try:
            fsbl_path = os.path.abspath(path)
            updatePlatformComponentRequest = platform_pb2.UpdatePlatformComponentRequest(platform_location = self.project_location, platform_name = self.project_name, fsbl_Path = fsbl_path, target_processor = None)
            self._stub.UpdatePlatformComponent(updatePlatformComponentRequest)
            return(True)
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="set_fsbl_elf failed", ex=e)
            
    def set_pmufw_elf(self, path):
        """
        set_pmufw_elf:
            Set the prebuilt pmufw elf to be used as boot component when boot
            components are removed.

        Prototype:
            status = platform.set_pmufw_elf(path = <path>)

        Optional Arguments:
            path = <path>
                Prebuilt pmufw.elf path.

        Returns:
            True
                PMUFW elf added successfully.
            Exception
                Could not add PMUFW elf.
                
        Examples:
            platform.set_pmufw_elf('/tmp/pmufw.elf')
        """
        try:
            pmufw_elf = os.path.abspath(path)
            updatePlatformComponentRequest = platform_pb2.UpdatePlatformComponentRequest(platform_location = self.project_location, platform_name = self.project_name, pmufw_Elf = pmufw_elf, target_processor = None)
            self._stub.UpdatePlatformComponent(updatePlatformComponentRequest)
            return(True)
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="set_fsbl_elf failed", ex=e)

    def retarget_fsbl(self, target_processor = None, domain_name = None):
        """
        retarget_fsbl:
            Regenrate fsbl for the specified processor type. This is valid only
            for ZU+.

        Prototype:
            status = platform.retarget_fsbl(target_processor = <target>,
                                             domain_name = <domain_name>)

        Optional Arguments:

            target_processor = <target>
                Processor for which the existing fsbl has to be
                re-generated.

            domain_name = <domain_name>

        Returns:
            True
                Fsbl generated succcessfully.
            Exception
                Fsbl could not be generated.

        Examples:
            platform.retarget_fsbl(target_processor = "psu_cortexr5_0")
        """
        try:
            retargetFSBLRequest = platform_pb2.ReTargetFSBLRequest(platform_location = self.project_location, domain_name = domain_name, target_processor = target_processor)
            response = self._stub.RetargetFSBL(retargetFSBLRequest)
            return(True)
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="retarget_fsbl failed", ex=e)

    # Commented out the unsupported methods for now

    def update_hw(self, hw = None, emulation_xsa_path = None):
        """
        update_hw:
            Update the platform to use a new hardware specification file
            specified.

        Prototype:
            status = platform.update_hw(hw = <hw_spec>,
                                        emulation_xsa_path = <xsa_path>)

        Required Arguments:
            hw = <hw_spec> or emulation_xsa_path = <xsa_path>
                Hardware specification file or emulation xsa path.

        Returns:
            True
                Hw specification updated successfully.
            Exception
                Hw specification could not be updated.

        Examples:
            platform.update_hw(hw = "/home/user/newdesign.xsa")
        """
        try:
            if(hw!=None and hw!=''):
                hw = os.path.abspath(hw)
            if(emulation_xsa_path!=None and emulation_xsa_path!=''):
                emulation_xsa_path = os.path.abspath(emulation_xsa_path)
            updatePlatformRequest = platform_pb2.UpdatePlatformRequest(xsa_path = hw, emulation_xsa_path = emulation_xsa_path, platform_location = self.project_location)
            response = self._stub.UpdateHwXSA(updatePlatformRequest)
            for updateStream in response:
                for logLine in updateStream.log:
                     print(logLine)
            return True
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="update_hw failed", ex=e)

    # def make_local(self):
    #     """
    #     make_local:
    #         Make the referenced SW components local to the platform.

    #     Prototype:
    #         status = platform.make_local()

    #     Arguments:
    #         None

    #     Returns:
    #         True
    #             Sw components made local successfully.
    #         Exception
    #             Sw components could not be made local.

    #     Examples:
    #         platform.make_local()
    #     """
    #     try:
    #         platformConfigRequest = platform_pb2.PlatformConfigRequest(project_name = self.project_name)
    #         response = self._stub.PlatformConfig(platformConfigRequest)
    #         return(response)
    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg="make_local failed", ex=e)

    # def generate_boot_files(self):
    #     """
    #     generate_boot_file:
    #         Generate boot components for the platform.

    #     Prototype:
    #         status = platform.generate_boot_files()

    #     Arguments:
    #         None

    #     Returns:
    #         True
    #             Boot components generated succcessfully.
    #         Exception
    #             Boot compoennts could not be generated.

    #     Examples:
    #         platform.generate_boot_file()
    #     """
    #     try:
    #         platformConfigRequest = components_pb2.PlatformConfigRequest(project_name = self.project_name)
    #         response = self._component_stub.PlatformConfig(platformConfigRequest)
    #         return(True)
    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg="generate_boot_files failed", ex=e)

    #TODO: How to accomodate fsbl-elf and pmufw-elf

    # def remove_boot_files(self):
    #     """
    #     remove_boot_file:
    #         Remove all the boot components generated during platform
    #         creation.

    #     Prototype:
    #         status = platform.remove_boot_files()

    #     Arguments:
    #         None

    #     Returns:
    #         True
    #             Boot components removed succcessfully.
    #         Exception
    #             Boot compoennts could not be removed.

    #     Examples:
    #         platform.remove_boot_file()
    #     """
    #     try:
    #         platformConfigRequest = components_pb2.PlatformConfigRequest(project_name = self.project_name)
    #         response = self._component_stub.PlatformConfig(platformConfigRequest)
    #         return(True)
    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg="remove_boot_files failed", ex=e)

    # TODO: Make two seperate methods for get/set extra compiler and linker flags
    # def extra_compiler_flags(self, param, value = None):
    #     """
    #     extra_compiler_flags:
    #         Set/get extra compiler flags for the specified parameter. If the
    #         value is not passed, the existing value will be returned. Only
    #         FSBL and PMUFW are the supported parameters.

    #     Prototype:
    #         status = platform.extra_compiler_flags(param = <FSBL/PMUFW>,
    #                                                 value = <value>)

    #     Required Arguments:
    #         param = <FSBL/PMUFW>
    #             Valid parameter options are "FSBL" and "PMUFW".

    #     Optional Arguments:
    #         value = <value>
    #             Value for the specified parameter.

    #     Returns:
    #         Value
    #             Current value for the specified parameter when no value is passed.
    #         True
    #             Extra compiler flags set succcessfully.
    #         Exception
    #             Compiler flags could not be set.

    #     Examples:
    #         platform.extra_compiler_flags("FSBL")
    #             Get the extra compiler flags. These are the flags added extra
    #             to the flags derived from the libraries, processor, and OS.
    #     """
    #     try:
    #         platformConfigRequest = platform_pb2.PlatformConfigRequest(project_name = self.project_name, param = param, value = value)
    #         response = self._stub.PlatformConfig(platformConfigRequest)
        #     return(response)
        # except grpc.RpcError as e:
        #     _utils.grpc_exception(msg="extra_compiler_flags failed", ex=e)

    # def extra_linker_flags(self, param, value = None):
    #     """
    #     extra_compiler_flags:
    #         Set/get extra linker flags for the specified parameter. If the
    #         value is not passed, the existing value will be returned. Only
    #         FSBL and PMUFW are the supported parameters.

    #     Prototype:
    #         status = platform.extra_linker_flags(param = <FSBL/PMUFW>,
    #                                                 value = <value>)

    #     Required Arguments:
    #         param = <FSBL/PMUFW>
    #             Valid parameter options are "FSBL" and "PMUFW".

    #     Optional Arguments:
    #         value = <value>
    #             Value for the specified parameter.

    #     Returns:
    #         Value
    #             Current value for the specified parameter when no value is passed.
    #         True
    #             Extra compiler flags set succcessfully.
    #         Exception
    #             Compiler flags could not be set.

    #     Examples:
    #         platform.extra_linker_flags("FSBL")
    #             Get the extra linker flags. These are the flags added extra
    #             to the flags derived from the libraries, processor, and OS.
    #     """
    #     try:
    #         platformConfigRequest = platform_pb2.PlatformConfigRequest(project_name = self.project_name, param = param, value = value)
    #         response = self._stub.PlatformConfig(platformConfigRequest)
        #     return(response)
        # except grpc.RpcError as e:
        #     _utils.grpc_exception(msg="extra_linker_flags failed", ex=e)

    # def reset_user_defined_flags(self):
    #     """
    #     reset_user_defined_flags:
    #         Resets the extra compiler and linker flags. Only FSBL and PMUFW are
    #         the supported parameters.

    #     Prototype:
    #         status = platform.reset_user_defined_flags()

    #     Arguments:
    #         None

    #     Returns:
    #         True
    #             User defined flags reset succcessfully.
    #         Exception
    #             Flags couldn't be reset.

    #     Examples:
    #         platform.reset_user_defined_flags()
    #     """
    #     try:
    #         platformConfigRequest = platform_pb2.PlatformConfigRequest(project_name = self.project_name)
    #         response = self._stub.platformConfig(platformConfigRequest)
    #         return(response)
    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg="reset_user_defined_flags failed", ex=e)

    # def report_param(self, param):
    #     """
    #     report_param:
    #         Return the list of extra compiler and linker flags set to the
    #         given parameter. Only FSBL and PMUFW are the supported parameters.

    #     Prototype:
    #         status = platform.report_param(param = <FSBL/PMUFW>)

    #     Required Arguments:
    #         param = <FSBL/PMUFW>
    #             Supported parameters are "FSBL" or "PMUFW".

    #     Returns:
    #         List of extra compiler and linker flags.

    #     Examples:
    #         platform.report_param("FSBL")
    #     """
    #     try:
    #         platformConfigRequest = platform_pb2.PlatformConfigRequest(project_name = self.project_name, param = param)
    #         response = self._stub.PlatformConfig(platformConfigRequest)
    #         return(response)
    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg="report_param failed", ex=e)

    def _clonePlatform(self, comp):
        try:
            self.__component_assign__(comp)
            return self

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="clone component failed", ex=e)

    def _getPlatformLocation(self, name, func):
        location = None
        if (self._server.checkWorkspaceSet()):
            workspace = self._server.getWorkspace(func)
            location = workspace + "/" + name
        else:
            _utils.exception(msg=f"{func}: Cannot get platform location for '{name}', no workspace is set")
        return location

    def _createPlatform(self, name, hw, desc, platform_os, cpu, domain_name, template, no_boot_bsp, fsbl_target, fsbl_path , pmufw_Elf, emulation_xsa_path, platform_xpfm_path, is_pmufw_req):

        try:
            location = self._getPlatformLocation(name, "create_platform_component")
            defaultXSAList = ["vck190", "vmk180", "zcu102", "zcu106", "zc702", "zc706"]
            if hw not in defaultXSAList and hw!='':
                hw = os.path.abspath(hw)
            if(emulation_xsa_path!=''):
                emulation_xsa_path = os.path.abspath(emulation_xsa_path)
            if(platform_xpfm_path!=''):
                platform_xpfm_path = os.path.abspath(platform_xpfm_path)
            createPlatformRequest = platform_pb2.CreatePlatformRequest(platform_name = name,
                                                                        platform_description = desc,
                                                                        platform_location = location,
                                                                        xsa_path = hw,
                                                                        os = platform_os,
                                                                        cpu = cpu,
                                                                        domain_name = domain_name,
                                                                        template = template,
                                                                        is_custom_fsbl = no_boot_bsp,
                                                                        fsbl_target = fsbl_target,
                                                                        fsbl_Path = fsbl_path,
                                                                        pmufw_Elf = pmufw_Elf,
                                                                        emulation_xsa_path = emulation_xsa_path,
                                                                        platform_xpfm_path = platform_xpfm_path,
                                                                        is_pmufw_req= is_pmufw_req)
            createResponse = self._stub.CreatePlatform(createPlatformRequest)
            for createStream in createResponse:
                for logLine in createStream.log:
                     print(logLine)

            getPlatformRequest = platform_pb2.GetPlatformRequest(platform_location = location)
            platform = self._stub.GetPlatform(getPlatformRequest)
            self.__assign__(platform)
            return self

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot create platform", ex=e)

    def _getProcessorOSList(self, xsa, platform):

        try:
            location = None
            if(platform != None):
                location = self._getPlatformLocation(platform, "get_processor_os_list")
            if(xsa != None):
                xsa = os.path.abspath(xsa)
            getProcessorOSListRequest = platform_pb2.GetProcessorOSListRequest(xsa_path = xsa,
                                                                               platform_location = location)
            os_list = self._stub.GetProcessorOSList(getProcessorOSListRequest)
            return os_list

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot get processor os list.", ex=e)

    def _getPlatform(self, name):

        try:
            location = self._getPlatformLocation(name, "get_platform_component")
            getPlatformRequest = platform_pb2.GetPlatformRequest(platform_location = location)
            platform = self._stub.GetPlatform(getPlatformRequest)
            self.__assign__(platform)
            return self

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot get platform", ex=e)

    def _listPlatformComponents(self):

        try:
            listPlatformsRequest = platform_pb2.ListPlatformComponentsRequest()
            platforms = self._stub.ListPlatformComponents(listPlatformsRequest)
            return platforms

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot list platform components", ex=e)

    def _deletePlatform(self, name):
        try:
            location = self._getPlatformLocation(name, "delete_platform_component")
            deleteComponentRequest = components_pb2.DeleteComponentRequest(component_location = location)
            self._component_stub.DeleteComponent(deleteComponentRequest)
            self = None
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot delete platform", ex=e)

    def _setSwRepo(self, level, path):
        try:
            workspace = ''
            if(level.upper() == 'LOCAL'):
                if(self._server.checkWorkspaceSet()):
                    level = platform_pb2.EmbeddedRepoType.WORKSPACE
                    workspace = self._server.getWorkspace('set_sw_repo')
                else:
                    _utils.exception(msg=f"set_sw_repo: Cannot set sw repo for '{level} level' \n\
                        \r, no workspace is set.")
            elif(level.upper() == 'GLOBAL'):
                level = platform_pb2.EmbeddedRepoType.USER
            else:
                _utils.exception(msg=f"set_sw_repo: Invalid level '{level}' \n\
                        \r, Valid levels are \'LOCAL\' and \'GLOBAL\'.")

            if(path!=[]):
                path = [os.path.abspath(p) for p in path]

            setEmbeddedRepoDataRequest = platform_pb2.SetEmbeddedRepoDataRequest(repo_level = level, repo_data = path, workspace_location = workspace)
            self._stub.SetEmbeddedRepoData(setEmbeddedRepoDataRequest)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot set sw repo", ex=e)

    def _getSwRepo(self, level):
        try:
            # Implementation in such a way that if no level is passed, repos at both the levels are returned
            workspace = ''
            repoDataList = []
            if(level.upper() == 'LOCAL' or level == ''):
                if(self._server.checkWorkspaceSet()):
                    repo_level = platform_pb2.EmbeddedRepoType.WORKSPACE
                    workspace = self._server.getWorkspace('get_sw_repo')
                    repoDataList = self._getSwRepoHelper(repo_level, workspace, repoDataList)
                else:
                    if(level!=''):
                        _utils.exception(msg=f"set_sw_repo: Cannot get sw repo for '{level} level' \n\
                            \r, no workspace is set.")
                    else:
                        print("\nCannot get local level sw repo as workspace is not set. Getting global level sw repo:")

            if(level.upper() == 'GLOBAL' or level == ''):
                repo_level = platform_pb2.EmbeddedRepoType.USER
                repoDataList = self._getSwRepoHelper(repo_level, workspace, repoDataList)
            else:
                if(level.upper()!='LOCAL'):
                    _utils.exception(msg=f"get_sw_repo: Invalid level '{level}' \n\
                        \r, Valid levels are \'LOCAL\' and \'GLOBAL\'.")

            return repoDataList

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot get sw repo", ex=e)

    def _getSwRepoHelper(self, level, workspace, repoList):
        try:
            getEmbeddedRepoDataRequest = platform_pb2.GetEmbeddedRepoDataRequest(repo_level = level, workspace_location = workspace)
            repoData = self._stub.GetEmbeddedRepoData(getEmbeddedRepoDataRequest)
            for r in repoData.repo_data:
                repoList.append(str(r))
            return repoList
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot get sw repo", ex=e)

    def _rescanSwRepo(self):
        try:
            if(self._server.checkWorkspaceSet()):
                path = self._server.getWorkspace('rescan_sw_repo')
            else:
                path = None
            generateEmbeddedDataResponse = platform_pb2.GenerateEmbeddedRepoDataRequest(location = path)
            repoMessage = self._stub.GenerateEmbeddedRepoData(generateEmbeddedDataResponse)
            return True
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot rescan sw repo", ex=e)
