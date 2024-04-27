import grpc
import platform_pb2_grpc
import platform_pb2
import bsp_pb2
from vitis import _utils
import textwrap
import os

class Domain(object):
    """
    Client Class for Vitis Project service.
    """

    def __init__(self, server):

        self._server = server
        self.stub = platform_pb2_grpc.PlatformStub(self._server.channel)

    def __assign__(self, domain):
        self.domain_name = domain.name
        self.platform_location = domain.platform_location

    def __str__(self) -> str:
        data = f"'domain_name': {self.domain_name}\n"
        data = data + f"'platform_location': '{self.platform_location}'\n"
        return (data)

    def __repr__(self):
        return (self.__str__())

    def report(self):
        """
        report:
            Display information of the domain.

        Prototype:
            domain.report()

        Arguments:
            None

        Returns:
            Prints information about the domain.

        Examples:
            domain1.report()
        """
        try:
            getDomainRequest = platform_pb2.GetDomainRequest(platform_location = self.platform_location,
                                                             name = self.domain_name)
            domain = self.stub.GetDomain(getDomainRequest)
            print("\nDomain details:\n")
            if (domain != None):
                print(f"Domain name         :  '{domain.name}'")
                print(f"Display name        :  '{domain.display_name}'")
                print(f"Platform location   :  '{domain.platform_location}'")
                print(f"Processor           :  '{domain.processor}'")
                print(f"OS                  :  '{domain.os}'")
                if(domain.qemu_args_file != ''):
                    print("QEMU args           :")
                    for w in textwrap.wrap(domain.qemu_args_file, width=60):
                        print(textwrap.indent(w, '                     ', lambda line: True))
                if(domain.pmc_args_file != ''):
                    print("PMC args            :")
                    for w in textwrap.wrap(domain.pmc_args_file, width=60):
                        print(textwrap.indent(w, '                     ', lambda line: True))
                if(domain.bif_file != ''):
                    print("BIF file            :")
                    for w in textwrap.wrap(domain.bif_file, width=60):
                        print(textwrap.indent(w, '                     ', lambda line: True))
                if(domain.boot_directory != ''):
                    print("Boot directory      :")
                    for w in textwrap.wrap(domain.boot_directory, width=60):
                        print(textwrap.indent(w, '                     ', lambda line: True))
                if(domain.sdcard_directory != ''):
                    print("SD directory        :")
                    for w in textwrap.wrap(domain.sdcard_directory, width=60):
                        print(textwrap.indent(w, '                     ', lambda line: True))

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="failed to get the domain", ex=e)

    # Domain config APIs

    # def update_desc(self, desc):
    #     """
    #     update_desc:
    #         Update the description of the domain.

    #     Prototype:
    #         status = domain.update_desc(desc = <description>)

    #     Required Arguments:
    #         desc = <description>
    #             Description of the domain.

    #     Returns:
    #         True
    #             Description updated successfully.
    #         Exception
    #             Description could not be updated.

    #     Examples:
    #         domain1.update_desc("Memory test application for Zynq")
    #     """
    #     try:
    #         UpdateDomainRequest = platform_pb2.UpdateDomainRequest(platform_location = self.platform_location, domain_name = self.domain_name, description = desc)
    #         response = self.stub.UpdateDomain(UpdateDomainRequest)
    #         return True
    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg="update_desc failed", ex=e)

    def update_name(self, new_name):
        """
        update_name:
            Update the name of the domain.

        Prototype:
            status = domain.update_name(name = <new_name>)

        Required Arguments:
            name = <new_name>
                New display name for the domain.

        Returns:
            True
                Name updated successfully.
            Exception
                Name could not be updated.

        Examples:
            domain1.update_name("zc702_MemoryTest")
        """
        try:
            UpdateDomainRequest = platform_pb2.UpdateDomainRequest(platform_location = self.platform_location,
                                                                   name = self.domain_name,
                                                                   display_name = new_name)
            response = self.stub.UpdateDomain(UpdateDomainRequest)
            return True
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="update_name failed", ex=e)

    def set_dtb(self, path):
        """
        set_dtb:
           Update the existing DTB file in boot components with a custom DTB file.

        Prototype:
            status = domain.set_dtb(path = <dtb_file>)

        Required Arguments:
            path = <dtb_file>
                Path for the custom DTB file.

        Returns:
            True
                Name updated successfully.
            Exception
                Name could not be updated.

        Examples:
            domain1.set_dtb("/tmp/dtb_file")
        """
        try:
            UpdateDomainRequest = platform_pb2.UpdateDomainRequest(platform_location = self.platform_location,
                                                                   name = self.domain_name,
                                                                   customDtb = path)
            self.stub.UpdateDomain(UpdateDomainRequest)
            return True
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="set_dtb failed", ex=e)

    def set_sd_dir(self, path):
        """
        set_sd_dir:
            For domain with Linux as OS, use pre-built Linux images from this
            directory, while creating the PetaLinux project. This option is
            valid only for Linux domains.

        Prototype:
            status = domain.set_sd_dir(path = <path>)

        Required Arguments:
            path = <path>
                Path for the pre-built linux image directory.

        Returns:
            True
                Sd-dir set updated successfully.
            Exception
                Sd-dir could not be set.

        Examples:
            domain1.set_sd_dir(path = "/home/user/linux_image/")
        """
        try:
            if(os.path.exists(path)):
                UpdateDomainRequest = platform_pb2.UpdateDomainRequest(platform_location = self.platform_location,
                                                                       name = self.domain_name,
                                                                       sdcard_directory = os.path.abspath(path))
                self.stub.UpdateDomain(UpdateDomainRequest)
                return True
            else:
                _utils.exception(msg=f" Invalid SD directory path '{path}'")
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="set_sd_dir failed", ex=e)

    # def generate_bif(self):
    #     """
    #     generate_bif:
    #         Generate a standard bif for the domain. Domain report shows the
    #         location of the generated bif. This option is valid only for
    #         Linux domains.

    #     Prototype:
    #         status = domain.generate_bif()

    #     Arguments:
    #         None

    #     Returns:
    #         True
    #             Bif generated successfully.
    #         Exception
    #             Bif could not be generate.

    #     Examples:
    #         domain1.generate_bif()
    #     """
    #     try:
    #         UpdateDomainRequest = platform_pb2.UpdateDomainRequest(platform_location = self.platform_location, name = self.domain_name)
    #         response = self.stub.UpdateDomain(UpdateDomainRequest)
    #         return(response)
    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg="generate_bif failed", ex=e)

    # def add_sw_repo(self, repo_list):
    #     """
    #     add_sw_repo:
    #         Add a list of repositories to be used to pick software components
    #         like drivers and libraries while generating this domain.

    #     Prototype:
    #         status = domain.add_sw_repo(repo_list = ["repo_path1",..]**)

    #     Required Arguments:
    #         repo_list = ["repo_path1",..]**
    #             List of repositories to be used to pick components while
    #             generating the domain.

    #     Returns:
    #         True
    #             sw_repo added successfully.
    #         Exception
    #             sw_repo could not be added.

    #     Examples:
    #         domain1.add_sw_repo(repo_list = ["/home/usr/lib"])
    #     """
    #     try:
    #         UpdateDomainRequest = platform_pb2.UpdateDomainRequest(platform_location = self.platform_location, name = self.domain_name, repo_list = repo_list)
    #         response = self.stub.UpdateDomain(UpdateDomainRequest)
    #         return True
    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg="add_sw_repo failed", ex=e)

    # def add_bsp_spec(self, file):
    #     """
    #     add_bsp_spec:
    #         Use bsp_spec from specified file, instead of generating spec file for
    #         the domain.

    #     Prototype:
    #         status = domain.add_bsp_spec(file = <bsp_spec_file>)

    #     Required Arguments:
    #         file = <bsp_spec_file>
    #             File containing bsp_spec.

    #     Returns:
    #         True
    #             bsp_spec added successfully.
    #         Exception
    #             bsp_spec could not be added.

    #     Examples:
    #         domain1.add_bsp_spec(file = "/home/usr/bsp_file")
    #     """
    #     try:
    #         UpdateDomainRequest = platform_pb2.UpdateDomainRequest(platform_location = self.platform_location, name = self.domain_name, file = file)
    #         response = self.stub.UpdateDomain(UpdateDomainRequest)
    #         return True
    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg="add_bsp_spec failed", ex=e)

    # def add_inc_path(self, path):
    #     """
    #     add_inc_path:
    #         Additional include path which should be added while building the
    #         application created for this domain..

    #     Prototype:
    #         status = domain.add_inc_path(path = <include_path>)

    #     Required Arguments:
    #         path = <include_path>
    #             Include path to be added.

    #     Returns:
    #         True
    #             Include path added successfully.
    #         Exception
    #             Include path could not be added.

    #     Examples:
    #         domain1.add_inc_path(path = "/home/usr/include_path1")
    #     """
    #     try:
    #         UpdateDomainRequest = platform_pb2.UpdateDomainRequest(platform_location = self.platform_location, name = self.domain_name, path = path)
    #         response = self.stub.UpdateDomain(UpdateDomainRequest)
    #         return True
    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg="add_inc_path failed", ex=e)

    # def add_lib_path(self, path):
    #     """
    #     add_lib_path:
    #         Additional library search path which should be added to the linker
    #         settings of the application created for this domain.

    #     Prototype:
    #         status = domain.add_inc_path(path = <library_path>)

    #     Required Arguments:
    #         path = <library_path>
    #             Library path to be added.

    #     Returns:
    #         True
    #             Library path added successfully.
    #         Exception
    #             Library path could not be added.

    #     Examples:
    #         domain1.add_lib_path(path = "/home/usr/lib_path")
    #     """
    #     try:
    #         UpdateDomainRequest = platform_pb2.UpdateDomainRequest(platform_location = self.platform_location, name = self.domain_name, path = path)
    #         response = self.stub.UpdateDomain(UpdateDomainRequest)
    #         return True
    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg="add_lib_path failed", ex=e)

    # def add_sysroot(self, sysroot_dir):
    #     """
    #     add_sysroot:
    #         The Linux sysroot directory that should be added to the platform.
    #         This sysroot will be consumed during application build.

    #     Prototype:
    #         status = domain.add_sysroot(sysroot_dir = <sysroot_dir>)

    #     Required Arguments:
    #         sysroot_dir = <sysroot_dir>
    #             Sysroot directory to be added.

    #     Returns:
    #         True
    #             Sysroot added successfully.
    #         Exception
    #             Sysroot could not be added.

    #     Examples:
    #         domain1.add_sysroot(path = "/home/usr/sysroot/aarch64-xilinx-linux")
    #     """
    #     try:
    #         UpdateDomainRequest = platform_pb2.UpdateDomainRequest(platform_location = self.platform_location, name = self.domain_name, sysroot_dir = sysroot_dir)
    #         response = self.stub.UpdateDomain(UpdateDomainRequest)
    #         return True
    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg="add_sysroot failed", ex=e)

    def add_boot_dir(self, path):
        """
        add_boot_dir:
            Add a directory to generate components after Linux image build.

        Prototype:
            status = domain.add_boot_dir(path = <boot_dir>)

        Required Arguments:
            path = <boot_dir>
                Path of boot directory to be added.

        Returns:
            True
                Boot directory added successfully.
            Exception
                Boot directory could not be added.

        Examples:
            domain1.add_boot_dir(path = "/home/boot_dir_1")
        """
        try:
            if(os.path.exists(path)):
                UpdateDomainRequest = platform_pb2.UpdateDomainRequest(platform_location = self.platform_location,
                                                                       name = self.domain_name,
                                                                       boot_directory = os.path.abspath(path))
                self.stub.UpdateDomain(UpdateDomainRequest)
                return True
            else:
                _utils.exception(msg=f" Invalid boot directory path '{path}'")
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="add_boot_dir failed", ex=e)

    def add_bif(self, path):
        """
        add_bif:
            Add a bif file tp be used to create boot image for Linux boot.

        Prototype:
            status = domain.add_bif(path = <file_path>)

        Required Arguments:
            path = <file_path>
                Bif file to be added.

        Returns:
            True
                Bif file added successfully.
            Exception
                Bif file could not be added.

        Examples:
            domain1.add_bif(path = "/home/boot/bif1")
        """
        try:
            if(os.path.exists(path)):
                UpdateDomainRequest = platform_pb2.UpdateDomainRequest(platform_location = self.platform_location,
                                                                       name = self.domain_name,
                                                                       bif_file = os.path.abspath(path))
                self.stub.UpdateDomain(UpdateDomainRequest)
                return True
            else:
                _utils.exception(msg=f" Invalid bif file path '{path}'")
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="add_bif failed", ex=e)

    def add_qemu_args(self, qemu_option, path):
        """
        add_args:
            Add file with all PS/PMC/PMU QEMU args listed.

        Prototype:
            status = domain.add_qemu_args(qemu_option = <"PS"/"PMC"/"PMU">
                                          path = <qemu_args_file_path>)

        Required Arguments:
            qemu_option = <"PS"/"PMC"/"PMU">
                Valid qemu option are "PS", "PMC" or "PMU".
            path = <qemu_args_file_path>
                Path of file with all pmu/pmc/ps qemu args listed.

        Returns:
            True
                Qemu file added successfully.
            Exception
                Qemu file could not be added.

        Examples:
            domain1.add_qemu_args(qemu_option = "PS",
                                  path = "/home/usr/qemu_args1")
        """
        try:
            if(os.path.exists(path)):
                file_name  = os.path.abspath(path)
                if(qemu_option.upper() == 'PS'):
                    updateDomainRequest = platform_pb2.UpdateDomainRequest(platform_location = self.platform_location, name = self.domain_name, qemu_args_file = file_name)
                elif(qemu_option.upper() == 'PMU' or qemu_option.upper() == 'PMC'):
                    updateDomainRequest = platform_pb2.UpdateDomainRequest(platform_location = self.platform_location, name = self.domain_name, pmc_args_file = file_name)
                else:
                    _utils.exception(msg=f" Invalid option '{qemu_option}'")
                self.stub.UpdateDomain(updateDomainRequest)
                return True
            else:
                _utils.exception(msg=f" Invalid QEMU file path '{path}'")
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="add_qemu_args failed", ex=e)

    def add_qemu_data(self, path):
        """
        add_qemu_data:
            Directory which has all the files listed in file-name provided
            as part of qemu-args and pmuqemu-args options.

        Prototype:
            status = domain.add_quemu_data(path = <qemu_data_dir>)

        Required Arguments:
            path = <qemu_data_dir>
                Path of directory containing all the files provided as a part
                of qemu-args.

        Returns:
            True
                Qemu data added successfully.
            Exception
                Qemu data could not be added.

        Examples:
            domain1.add_qemu_data(path = "/home/usr/quemu_dir1")
        """
        try:
            if(os.path.exists(path)):
                data_dir  = os.path.abspath(path)
                UpdateDomainRequest = platform_pb2.UpdateDomainRequest(platform_location = self.platform_location, name = self.domain_name, qemudata = data_dir)
                self.stub.UpdateDomain(UpdateDomainRequest)
                return True
            else:
                _utils.exception(msg=f" Invalid QEMU data directory path '{path}'")

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="add_qemu_data failed", ex=e)

    # BSP settings
    def set_config(self, option, param, value, lib_name = None):
        """
        set_config:
            Set value to the configurable parameters.

        Prototype:
            status = domain.set_config(option = <option>,
                                       param = <key>,
                                       value = <value>,
                                       lib_name = <lib_name>)

        Required Arguments:
            option = <"lib"/"os"/"proc">
                Valid options are "lib"/"os"/"proc".
            param = <key>
                Parameter for which value is to be set.
                list_param("lib"/"os"/"proc") to get the list of configurable
                parameters.
            value = <value>
                Value for the parameter.

        Optional Arguments:
            lib_name = <lib_name>
                Library name in case 'lib' option is selected.

        Returns:
            True
                Configuration parameter set successfully.
            Exception
                Configuration parameter could not be set.

        Examples:
                domain1.set_config(option = 'os', param = "standalone_stdout",
                                    value = "uart0")
                domain1.set_config(option = 'os', param =
                                   "standalone_hypervisor_guest",
                                    value = True)
        """
        try:
            param_value = [param + ":\'" + str(value) + "\'"]
            BSPDataRequest = bsp_pb2.BSPDataRequest(platform_location = self.platform_location, domain_name = self.domain_name)

            if(option.lower() == 'os' or option.lower() == 'proc'):
                if(option.lower() == 'os'):
                    option = bsp_pb2.BSPPropertyType.TYPE_OS
                else:
                    option = bsp_pb2.BSPPropertyType.TYPE_PROCESSOR
                updateParamsRequest = bsp_pb2.BSPParameterUpdateRequest(bspDataRequest = BSPDataRequest, bsp_property_type = option, parameters = param_value)
                self.stub.UpdateBSPParameter(updateParamsRequest)

            elif(option == 'lib'):
                updateParamsRequest = bsp_pb2.BSPLibraryParameterUpdateRequest(bspDataRequest = BSPDataRequest, bsp_library_name = lib_name, parameters = param_value)
                self.stub.UpdateBSPLibraryParameter(updateParamsRequest)

            else:
                _utils.exception(msg=f"set_config: Invalid option provided. \n\
                \rValid options are lib, os and proc.")
            return True
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="set_config failed", ex=e)

    def get_config(self, option, param, lib_name = None):
        """
        get_config:
            Get value to the configurable parameters.

        Prototype:
            value = domain.get_config(option = <option>,
                                      param = <param>,
                                      lib_name = <lib_name>)

        Required Arguments:
            option = <"lib"/"os"/"proc">
                Valid options are "lib"/"os"/"proc".
            param = <param>
                Use list_param("lib"/"os"/"proc") to get the list of
                configurable parameters.

        Optional Arguments:
            lib_name = <lib_name>
                Library name in case 'lib' option is selected.

        Returns:
            Value
                Current value for the parameter.

        Examples:
            value = domain1.get_config(option = "os",
                                       param = "standalone_stdin")
        """
        try:
            BSPDataRequest = bsp_pb2.BSPDataRequest(platform_location = self.platform_location, domain_name = self.domain_name)

            if(option.lower() == 'os' or option.lower() == 'proc'):
                if(option.lower() == 'os'):
                    option = bsp_pb2.BSPPropertyType.TYPE_OS
                else:
                    option = bsp_pb2.BSPPropertyType.TYPE_PROCESSOR
                getParamsRequest = bsp_pb2.BSPParameterDataRequest(bspDataRequest = BSPDataRequest, bsp_property_type = option, parameter_name = param)
                param = self.stub.GetBSPParameter(getParamsRequest)

            elif(option == 'lib'):
                getParamsRequest = bsp_pb2.BSPLibraryParameterDataRequest(bspDataRequest = BSPDataRequest, bsp_library_name = lib_name, parameter_name = param)
                param = self.stub.GetBSPLibraryParameter(getParamsRequest)

            else:
                _utils.exception(msg=f"get_config: Invalid option provided. \n\
                \rValid options are lib, os and proc.")

            print(f"\nParameter name      :  '{param.name}'")
            print(f"Description         :  '{param.description}'")
            print(f"Default value       :  '{param.default_value}'")
            print(f"Value               :  '{param.value}'")
            print(f"Possible options    :  '{param.possibleOptions}'")
            print(f"DataType            :  '{param.dataType}'")
            print(f"Permission          :  '{param.permission}'")
            paramDict = dict()
            paramDict['parameter_name'] = param.name
            paramDict['description']  = param.description
            paramDict['default_value'] = param.default_value
            paramDict['value'] =  param.value
            paramDict['possible_options'] =  param.possibleOptions
            paramDict['datatype'] = param.dataType
            paramDict['permission'] = param.permission
            return paramDict
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_config failed", ex=e)

    def get_drivers(self):
        """
        get_drivers:
            List the IPs and drivers assigned to the IPs in BSP.

        Prototype:
            drivers = domain.get_drivers()

        Arguments:
            None

        Returns:
            Drivers
                List of IPs and drivers.

        Examples:
            drivers = domain1.get_drivers()
        """
        try:
            getDriversRequest = bsp_pb2.BSPDataRequest(platform_location = self.platform_location, domain_name = self.domain_name)
            drivers = self.stub.GetDrivers(getDriversRequest)
            print("\nList of drivers assigned:")
            i = 1
            driversList = list()
            for d in drivers.driver:
                driverDict = dict()
                print("\nDriver ",i,":")
                i = i+1
                print(f"Name                :  '{d.name}'")
                print(f"IP type             :  '{d.ip_type}'")
                driverDict['name'] = d.name
                driverDict['ip_type'] = d.ip_type
                if(d.value):
                    driverDict['path'] = d.value
                    wrapped_value = textwrap.wrap(d.value +"'", width=60)
                    print(f"Path                :  '{wrapped_value[0]}")
                    for w in wrapped_value[1:]:
                        print(textwrap.indent(w, '                        ', lambda line: True))
                driversList.append(driverDict)
            return driversList
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_drivers failed", ex=e)

    def get_libs(self):
        """
        get_libs:
            List libraries added in the BSP settings.

        Prototype:
            libs = domain.get_libs()

        Arguments:
            None

        Returns:
            Libraries
                Return the list of libraries added in bsp settings of the domain.

        Examples:
            domain1.get_libs()
        """
        try:
            BSPDataRequest = bsp_pb2.BSPDataRequest(platform_location = self.platform_location, domain_name = self.domain_name)
            libs = self.stub.GetConfiguredLibraries(BSPDataRequest)
            index = 1
            print("\nList of configured libraries:")
            libsList = list()
            for lib in libs.library:
                libDict = dict()
                print("\nLibrary ",index,":")
                index = index+1
                print(f"Name                :  '{lib.name}'")
                libDict['name'] = lib.name
                if(lib.description):
                    libDict['description'] = lib.description
                    wrapped_desc = textwrap.wrap(lib.description +"'", width=60)
                    print(f"Description         :  '{wrapped_desc[0]}")
                    for w in wrapped_desc[1:]:
                        print(textwrap.indent(w, '                        ', lambda line: True))
                if(lib.current_path):
                    libDict['current_path'] = lib.current_path
                    print(f"Current path         :  '{lib.current_path}")
                libsList.append(libDict)
            return libsList
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_libs failed", ex=e)

    def get_os(self):
        """
        get_os:
            Display OS details from BSP settings.

        Prototype:
            os_details = domain.get_os()

        Arguments:
            None

        Returns:
            Current OS.

        Examples:
            os_details = domain1.get_os()
        """
        try:
            osDict = dict()
            BSPDataRequest = bsp_pb2.BSPDataRequest(platform_location = self.platform_location, domain_name = self.domain_name)
            response = self.stub.GetBSPData(BSPDataRequest)
            print(f"OS                  :  '{response.os.name}'")
            osDict['os'] = response.os.name
            if(response.os.current_path):
                osDict['current_path'] = response.os.current_path
                wrapped_desc = textwrap.wrap(response.os.current_path +"'", width=60)
                print(f"Current path        :  '{wrapped_desc[0]}")
                for w in wrapped_desc[1:]:
                    print(textwrap.indent(w, '                        ', lambda line: True))
            if(response.os.possibleOptions):
                osDict['possibleOptions'] = response.os.possibleOptions
                wrapped_desc = textwrap.wrap(response.os.possibleOptions[0] +"'", width=60)
                print(f"Available paths     :  '{wrapped_desc[0]}'")
                for w in wrapped_desc[1:]:
                    print(textwrap.indent(w, '                        ', lambda line: True))
                for paths in response.os.possibleOptions[1:]:
                    wrapped_desc = textwrap.wrap(paths +"'", width=60)
                    print(f"                    :  '{wrapped_desc[0]}'")
                    for w in wrapped_desc[1:]:
                        print(textwrap.indent(w, '                        ', lambda line: True))
            return osDict
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_os failed", ex=e)

    def list_params(self, option, lib_name = None):
        """
        list_params:
            List the configurable parameters of the <option>.

        Prototype:
            params = domain.list_params(option = <"lib"/"os"/"proc">,
                                        lib_name = <lib_name>)

        Required Arguments:
            option = <"lib"/"os"/"proc">
                Valid options are "lib"/"os"/"proc".

        Optional Arguments:
            lib_name = <lib_name>
                Library name if 'lib' option is selected.

        Returns:
            List of configurable parameters.

        Examples:
            params = domain1.list_params(option = "os")
                Return the configurable parameters of the OS in BSP.
        """
        try:
            BSPDataRequest = bsp_pb2.BSPDataRequest(platform_location = self.platform_location, domain_name = self.domain_name)

            if(option.lower() == 'os' or option.lower() == 'proc'):
                if(option.lower() == 'os'):
                    option = bsp_pb2.BSPPropertyType.TYPE_OS
                else:
                    option = bsp_pb2.BSPPropertyType.TYPE_PROCESSOR
                listParamsRequest = bsp_pb2.BSPParameterRequest(bspDataRequest = BSPDataRequest, bsp_property_type = option)
                response = self.stub.ListBSPParameters(listParamsRequest)

            elif(option == 'lib'):
                if(lib_name == None):
                    _utils.exception(msg=f"list_params: Provide a valid library name.")
                listParamsRequest = bsp_pb2.BSPLibraryRequest(bspDataRequest = BSPDataRequest, bsp_library_name = lib_name)
                response = self.stub.ListBSPLibraryParameters(listParamsRequest)

            else:
                _utils.exception(msg=f"list_params: Invalid option provided. \n\
                \rValid options are lib, os and proc.")
            print(f"\nList of parameters:")
            paramsList = list()
            i = 1
            for param in response.parameter:
                print(f"\nParameter ",i,":")
                i = i+1
                print(f"Parameter name      :  '{param.name}'")
                print(f"Description         :  '{param.description}'")
                print(f"Default value       :  '{param.default_value}'")
                print(f"Value               :  '{param.value}'")
                print(f"Possible options    :  '{param.possibleOptions}'")
                print(f"DataType            :  '{param.dataType}'")
                print(f"Permission          :  '{param.permission}'")
                paramDict = dict()
                paramDict['parameter_name'] = param.name
                paramDict['description']  = param.description
                paramDict['default_value'] = param.default_value
                paramDict['value'] =  param.value
                paramDict['possible_options'] =  param.possibleOptions
                paramDict['datatype'] = param.dataType
                paramDict['permission'] = param.permission
                paramsList.append(paramDict)
            return paramsList
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="list_params failed", ex=e)

    def regenerate(self):
        """
        regenerate:
            Regenerate BSP sources.

        Prototype:
            status = domain.regenerate()

        Arguments:
            None

        Returns:
            True
                BSP sources regenerated successfully.
            Exception
                Could not regenerate BSP sources.

        Examples:
            domain1.regenerate()
        """
        try:
            regenerateRequest = bsp_pb2.RegenerateBSPRequest(platform_location = self.platform_location, domain_name = self.domain_name)
            response = self.stub.RegenerateBSP(regenerateRequest)
            retStatus = None
            for buildStream in response:
                retStatus = buildStream.type
                for logLine in buildStream.log:
                    print(logLine)
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="regenerate failed", ex=e)

    # def reload(self):
    #     """
    #     reload:
    #         Revert to the earlier saved BSP settings.

    #     Prototype:
    #         status = domain.reload()

    #     Arguments:
    #         None

    #     Returns:
    #         True
    #             Settings reverted successfully.
    #         Exception
    #             Failed to revert to the earlier settings.

    #     Examples:
    #         domain1.reload()
    #     """
    #     try:
    #         reloadRequest = platform_pb2.ReloadRequest(name = self.domain_name)
    #         response = self.stub.Reload(reloadRequest)
    #         return(response)
    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg="reload failed", ex=e)

    # def set_driver(self, driver_name, ip, version):
    #     """
    #     set_driver:
    #         Set specified driver to the IP core in BSP settings of active
    #         domain.

    #     Prototype:
    #         status = domain.set_driver()

    #     Required Arguments:
    #         driver_name = <driver_name>
    #             Driver to be assigned to an IP.
    #         ip = <ip_name>
    #             IP instance for which the driver has to be added.
    #         version = <version>
    #             Driver version.

    #     Returns:
    #         True
    #             Driver set successfully.
    #         Exception
    #             Driver couldn't be set.

    #     Examples:
    #         domain1.set_driver(driver_name = "generic", ip = "ps7_uart_1",
    #                             version = 2.0)
    #             Set the generic driver for the ps7_uart_1 IP instance for the
    #             BSP.
    #     """
    #     try:
        #     setDriverRequest = platform_pb2.SetDriverRequest(name = self.domain_name, driver_name = driver_name, ip = ip, version = version)
        #     response = self.stub.SetDriver(setDriverRequest)
        #     return True
        # except grpc.RpcError as e:
        #     _utils.grpc_exception(msg="set_driver failed", ex=e)

    def set_lib(self, lib_name, path = None):
        """
        set_lib:
            Adds the library to the BSP settings. The newly added libraries
            become available to the application projects after the platform is
            generated.

        Prototype:
            status = domain.set_lib(lib_name = <lib_name>,
                                    path = <lib_path>)

        Required Arguments:
            lib_name = <lib_name>
                Library to be added to the BSP settings.

        Optional Arguments:
            path = <lib_path>
                BSP library path.

        Returns:
            True
                Library added successfully.
            Exception
                Failed to add the library.

        Examples:
            domain1.set_lib(lib_name = "xilffs", path = '/tmp/xilffs_5.0')
        """
        try:
            BSPDataRequest = bsp_pb2.BSPDataRequest(platform_location = self.platform_location, domain_name = self.domain_name)
            addBSPLibrary = bsp_pb2.BSPLibraryRequest(bspDataRequest = BSPDataRequest, bsp_library_name  = lib_name, bsp_library_path = path)
            self.stub.AddBSPLibrary(addBSPLibrary)
            return True
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="set_lib failed", ex=e)

    def update_path(self, option, name, new_path):
        """
        update_path:
            Update OS/Driver/Library path.

        Prototype:
            status = domain.update_path(option = <'OS'/'DRIVER'/'LIB'>,
                                        name = <OS/Driver/Library name>,
                                        new_path = <OS/Driver/Library path>)

        Required Arguments:
            option = <'OS'/'DRIVER'/'LIBRARY'>
                Valid options are 'OS', 'DRIVER' and 'LIB'.
            name = <OS/Driver/Library name>
                Name of the OS/Driver/Library.
            new_path = <OS/Driver/Library path>
                New path to be set for the mentioned OS/Driver/Library.

        Returns:
            True
                Path updated successfully.
            Exception
                Path could not be updated.

        Examples:
            domain1.update_path(option = 'LIB',lib_name = "xilffs",
                                new_path = '/tmp/xilffs_5.0')
        """
        try:
            BSPDataRequest = bsp_pb2.BSPDataRequest(platform_location = self.platform_location, domain_name = self.domain_name)

            if(option.lower() == 'os'):
                option = bsp_pb2.BSPPropertyType.TYPE_OS

            elif(option.lower() == 'driver'):
                option = bsp_pb2.BSPPropertyType.TYPE_DRIVER

            elif(option.lower() == 'lib' or option.lower() == 'library'):
                option = bsp_pb2.BSPPropertyType.TYPE_LIBRARY

            else:
                _utils.exception(msg=f"update_path: Invalid option provided. \n\
                \rValid options are 'lib', 'os' and 'driver'.")

            bspUpdatePathRequest = bsp_pb2.BSPUpdatePathRequest(bspDataRequest = BSPDataRequest, bsp_path_request_name = name, bsp_updated_path = new_path, bsp_property_type = option)
            self.stub.UpdateBSPPropertyPath(bspUpdatePathRequest)
            return True
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="update_path failed", ex=e)


    def remove_lib(self, lib_name):
        """
        remove_lib:
            Remove the library from BSP settings of the active domain.
            The library settings will come into effect only when the
            platform is generated.

        Prototype:
            status = domain.remove_lib(lib_name = <lib_name>)

        Required Arguments:
            lib_name = <lib_name>
                Library to be added to the BSP settings.

        Returns:
            True
                Library removed successfully.
            Exception
                Library could not be removed.

        Examples:
            domain1.remove_lib(lib_name = "xilffs")
        """
        try:
            BSPDataRequest = bsp_pb2.BSPDataRequest(platform_location = self.platform_location, domain_name = self.domain_name)
            removeBSPLibrary = bsp_pb2.BSPLibraryRequest(bspDataRequest = BSPDataRequest, bsp_library_name  = lib_name)
            response = self.stub.RemoveBSPLibrary(removeBSPLibrary)
            return True
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="remove_lib failed", ex=e)

    def generate_bif(self):
        """
        generate_bif:
            Generate a standard bif for the domain. Domain report shows the
            location of the generated bif. This option is valid only for
            Linux domains.

        Prototype:
            status = domain.generate_bif()

        Arguments:
            None

        Returns:
            True
                Bif generated successfully.
            Exception
                Bif file could not be generated.

        Examples:
            domain1.generate_bif()
        """
        try:
            generateBifRequest = platform_pb2.GenerateBifRequest(platform_location = self.platform_location, domain_name = self.domain_name)
            self.stub.GenerateBif(generateBifRequest)
            return True
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="generate_bif failed", ex=e)

    # def set_os_version(self, version):
    #     """
    #     set_os_version:
    #         Set OS version in the BSP settings of the domain.
    #         Latest version is added by default.

    #     Prototype:
    #         status = domain.set_os_version(version = <os_version>)

    #     Required Arguments:
    #         version = <os_version>
    #             OS version.

    #     Returns:
    #         True
    #             OS version set successfully.
    #         Exception
    #             OS version could not be removed.

    #     Examples:
    #         domain1.set_os_version(version = 6.6)
    #     """
    #     try:
    #         setOsVersionRequest = platform_pb2.SetOsVersionRequest(name = self.domain_name)
    #         response = self.stub.SetOsVersion(setOsVersionRequest)
    #         return True
    #     except grpc.RpcError as e:
    #         _utils.grpc_exception(msg="set_os_version failed", ex=e)

    def get_applicable_libs(self):
        """
        get_applicable_libs:
            Get list of libraries applicable for the current domain.

        Prototype:
            libs = domain.get_applicable_libs()

        Arguments:
            None

        Returns:
            List of applicable libraries.

        Examples:
            domain1.get_applicable_libs()
        """
        try:
            BSPDataRequest = bsp_pb2.BSPDataRequest(platform_location = self.platform_location, domain_name = self.domain_name)
            libs = self.stub.GetSupportedLibraries(BSPDataRequest)
            index = 1
            print("\nList of libraries:")
            for lib in libs.library:
                print("\nLibrary ",index,":")
                index = index+1
                print(f"Name                :  '{lib.name}'")
                if(lib.description):
                    wrapped_desc = textwrap.wrap(lib.description +"'", width=60)
                    print(f"Description         :  '{wrapped_desc[0]}")
                    for w in wrapped_desc[1:]:
                        print(textwrap.indent(w, '                        ', lambda line: True))
                if(lib.paths):
                    paths = ', '.join([paths.split(':')[0] for paths in lib.paths])
                    wrapped_desc = textwrap.wrap(paths +"'", width=60)
                    print(f"Available paths     :  '{wrapped_desc[0]}")
                    for w in wrapped_desc[1:]:
                        print(textwrap.indent(w, '                        ', lambda line: True))
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_applicable_libs failed", ex=e)
