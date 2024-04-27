import grpc
import linkerscript_pb2
import linkerscript_pb2_grpc
from vitis import _utils

class Ldfile(object):
    """
    Client Class for Linker script file.
    """

    def __init__(self, serverObj):

        self._server = serverObj
        self._stub = linkerscript_pb2_grpc.LinkerScriptStub(self._server.channel)

    #copy grpc object to wrapper object
    def __assign__(self, ldfile):
        self.file_path = ldfile

    def __str__(self) -> str:
        data = f"'file_path': '{self.file_path}'\n"
        return (data)

    def __repr__(self):
        return (self.__str__())

    def add_memory_region(self, name, base_address, size):
        """
        add_memory_region:
            Add a memory region in the linker script.

        Prototype:
            status = ldfile.add_memory_region(name = <name>,
                                              base_address = <base_addres>,
                                              size = <size>)

        Required Arguments:

            name = <name>
                Name for the new memory region.
            base_address = <base_address>
                Base address for the memory region.
            size = <size>
                Size of the memory region.

        Returns:
            True
                Added a memory region.
            Exception
                Memory region could not be added.

        Examples:
            status = ldfile.add_memory_region(name = <name>,
                                              base_address = <base_addres>,
                                              size = <size>)
        """
        try:
            request = linkerscript_pb2.AddMemoryRegionRequest(path = self.file_path,
                                                              name = name,
                                                              base_address = base_address,
                                                              size = size)
            self._stub.addMemoryRegion(request)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="add_memory_region failed", ex=e)

    def get_memory_regions(self):
        """
        get_memory_region:
            Get a memory regions in the linker script.

        Prototype:
            status = ldfile.get_memory_region()

        Arguments:
            None

        Returns:
            List of Memory regions existing in the linker script.

        Examples:
            status = ldfile.get_memory_regions()
        """
        try:
            request = linkerscript_pb2.FilePathOrContents(path = self.file_path)
            model = self._stub.getModel(request)
            modelList = list()
            if(model!=None):
                print(f"\nMemory regions :\n")
                for memory_region in model.memory_regions:
                    print(f"name              :  '{memory_region.name}'")
                    print(f"base_address      :  '{memory_region.base_address}'")
                    print(f"size              :  '{memory_region.size}'\n")
                    memoryRegionDict = dict()
                    memoryRegionDict['name'] = memory_region.name
                    memoryRegionDict['base_address'] = memory_region.base_address
                    memoryRegionDict['size'] = memory_region.size
                    modelList.append(memoryRegionDict)
            return modelList
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_memory_region failed", ex=e)

    def update_memory_region(self, name, base_address, size):
        """
        update_memory_region:
            Update an existing memory region in the linker script.

        Prototype:
            status = ldfile.update_memory_region(name = <name>,
                                              base_address = <base_addres>,
                                              size = <size>)

        Required Arguments:

            name = <name>
                Name for the new memory region to be updated.
            base_address = <base_address>
                New base address for the memory region.
            size = <size>
                New size for the memory region.

        Returns:
            True
                Updated the memory region.
            Exception
                Memory region could not be updated.

        Examples:
            status = ldfile.update_memory_region(name = <name>,
                                                 base_address = <base_addres>,
                                                 size = <size>)
        """
        try:
            request = linkerscript_pb2.UpdateMemoryRegionRequest(path = self.file_path,
                                                                 name = name,
                                                                 base_address = base_address,
                                                                 size = size)
            self._stub.updateMemoryRegion(request)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="update_memory_region failed", ex=e)

    def set_stack_size(self, size):
        """
        set_stack_size:
            Update the stack size in the linker script.

        Prototype:
            status = ldfile.set_stack_size(size = <stack_size>)

        Required Arguments:
            size = <stack_size>
                New size for the memory region.

        Returns:
            True
                Updated the stack size.
            Exception
                Stack size could not be updated.

        Examples:
            status = ldfile.set_stack_size(size = <stack_size>)
        """
        try:
            request = linkerscript_pb2.SetStackSizeRequest(path = self.file_path,
                                                           size = size)
            self._stub.setStackSize(request)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="set_stack_size failed", ex=e)

    def get_stack_size(self):
        """
        get_stack_size:
            Get the stack size in the linker script.

        Prototype:
            status = ldfile.get_stack_size(size = <stack_size>)

        Arguments:
            None

        Returns:
            Stack size

        Examples:
            status = ldfile.get_stack_size(size = <stack_size>)
        """
        try:
            request = linkerscript_pb2.FilePathOrContents(path = self.file_path)
            model = self._stub.getModel(request)
            return model.stack_size

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_stack_size failed", ex=e)

    def set_heap_size(self, size):
        """
        set_heap_size:
            Update the heap size in the linker script.

        Prototype:
            status = ldfile.set_heap_size(size = <heap_size>)

        Required Arguments:
            size = <heap_size>
                New size for the memory region.

        Returns:
            True
                Updated the heap size.
            Exception
                Heap size could not be updated.

        Examples:
            status = ldfile.set_heap_size(size = <heap_size>)
        """
        try:
            request = linkerscript_pb2.SetHeapSizeRequest(path = self.file_path,
                                                           size = size)
            self._stub.setHeapSize(request)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_heap_size failed", ex=e)

    def get_heap_size(self):
        """
        get_heap_size:
            Get the heap size in the linker script.

        Prototype:
            status = ldfile.get_heap_size()

        Arguments:
            None

        Returns:
            Heap size

        Examples:
            status = ldfile.get_heap_size()
        """
        try:
            request = linkerscript_pb2.FilePathOrContents(path = self.file_path)
            model = self._stub.getModel(request)
            return model.heap_size

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_heap_size failed", ex=e)

    def get_ld_sections(self):
        """
        get_ld_sections:
            Get a section maps in the linker script.

        Prototype:
            status = ldfile.get_ld_sections()

        Arguments:
            None

        Returns:
            List of section maps.

        Examples:
            status = ldfile.get_ld_sections()
        """
        try:
            request = linkerscript_pb2.FilePathOrContents(path = self.file_path)
            model = self._stub.getModel(request)
            if(model!=None):
                print(f"\nLD sections :\n")
                for section in model.section_maps:
                    print(f"region            :  '{section.region}'")
                    print(f"section           :  '{section.section}'\n")

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_ld_sections failed", ex=e)

    def update_ld_section(self, section, region):
        """
        update_ld_section:
            Update an existing section in the linker script.

        Prototype:
            status = ldfile.update_ld_section(section = <section>,
                                              region = <memory_region>)

        Required Arguments:
            section = <section>
                An existing memory code section identifier.
            region = <memory_region>
                The updated memory region for the code section.

        Returns:
            True
                Updated the ld section map.
            Exception
                Section map could not be updated.

        Examples:
            status = ldfile.update_ld_section()
        """
        try:
            section = [section]
            request = linkerscript_pb2.UpdateSectionMapRequest(path = self.file_path,
                                                              sections = section,
                                                              region = region)
            self._stub.updateSectionMap(request)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="update_ld_sections failed", ex=e)

    def regenerate(self):
        """
        regenerate:
            Regenerate the linker script with default values.

        Prototype:
            status = ldfile.regenerate()

        Arguments:
            None

        Returns:
            True
                Successfully regenerated the linker script.
            Exception
                Failed to regenerate the linker script.

        Examples:
            status = ldfile.regenerate()
        """
        try:
            request = linkerscript_pb2.RegenerateLinkerScriptRequest(path = self.file_path)
            self._stub.regenerateWithDefaults(request)
            return True

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="regenerate failed", ex=e)