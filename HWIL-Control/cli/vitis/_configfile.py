import grpc
import config_pb2_grpc
import config_pb2
import os
from vitis import _utils


class ConfigFile(object):
    def __init__(self, config_service, path):
        self.config_service = config_service
        self.path = os.path.abspath(path)

    def __assign__(self, config_file):
        self.config_service = config_file.config_service
        self.path = config_file.path

    def __str__(self) -> str:
        data = f"{self.path}"
        return (data)

    def get_sections(self):
        """
        get_sections:
            Get the section names from a config file.

        Prototype:
            status = cfg.get_sections()

        Required Arguments:
            None

        Returns:
            The list of sections in the config file.

        Examples:
            cfg.get_sections()
        """

        try:
            request = config_pb2.GetSectionsRequest(path = self.path)
            response = self.config_service.GetSections(request)
            return response.sections

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_sections failed", ex=e)


    def get_value(self, section = '', key = ''):
        """
        get_value:
            Get the value of the key in a specific section of a config file.

        Prototype:
            value = cfg.get_value(section=<config_section>, key=<key>)

        Required Arguments:
            section = "section"
                The name of the config file section, or an empty string for a top-level setting.
            key = "debug"
                The key portion of a key=value assignment

        Returns:
            The value of the assignment in the specified section, or an empty string.

        Examples:
            value = cfg.get_value(section='compiler', key='debug')
        """
        try :
            request = config_pb2.GetValueRequest(path = self.path, section = section, key = key)
            response = self.config_service.GetValue(request)
            return response.value

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_value failed", ex=e)

    def get_values(self, section = '', key = ''):
        """
        get_values:
            Return all values assigned wtih the key in a specific section of a config file.

        Prototype:
            values = cfg.get_values(section=<config_section>, key=<key>)

        Required Arguments:
            section = "section"
                The name of the config file section, or an empty string for a top-level setting.
            key = "include"
                The key portion of a key=value assignment

        Returns:
            The list of values of the assignment in the specified section, or an empty array if none.

        Examples:
            values = cfg.get_values(section='compiler', key='include')
        """
        try :
            request = config_pb2.GetValuesRequest(path = self.path, section = section, key = key)
            response = self.config_service.GetValues(request)
            return response.values

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_values failed", ex=e)

    def get_lines(self, section = '', key = ''):
        """
        get_lines:
            Return all assignment lines using wtih the key in a specific section of a config file.

        Prototype:
            lines = cfg.get_lines(section=<config_section>, key=<key>)

        Required Arguments:
            section = "section"
                The name of the config file section, or an empty string for a top-level setting.
            key = "include"
                The key portion of a key=value assignment

        Returns:
            A list of assignments using the key in the specified section, or an empty array if none.

        Examples:
            lines = cfg.get_lines(section='compiler', key='include')
        """
        try :
            request = config_pb2.GetLinesRequest(path = self.path, section = section, key = key)
            response = self.config_service.GetLines(request)
            return response.lines

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="get_lines failed", ex=e)

    def set_value(self, section = '', key = '', value = ''):
        """
        set_value:
            Set the value of the key in a specific section of a config file.
            Any earlier values for the key will be removed.

        Prototype:
            cfg.set_value(section=<config_section>, key=<key>, value=<value>)

        Required Arguments:
            section = "section"
                The name of the config file section, or an empty string for a top-level setting.
            key = "debug"
                The key portion of a key=value assignment
            value = "value"
                The new value for the key

        Returns:
            Nothing

        Examples:
            cfg.set_value(section='compiler', key='debug', value='false')
        """
        try :
            request = config_pb2.SetValueRequest(path = self.path, section = section, key = key, value = value)
            response = self.config_service.SetValue(request)
            return response

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="set_value failed", ex=e)

    def set_values(self, section = '', key = '', values = []):
        """
        set_values:
            Set repeated values for the key in a specific section of a config
            file. This will add one key=value assignment for each value. Any 
            earlier values for the key will be removed.

        Prototype:
            cfg.set_values(section = <config_section>, key = <key>, 
                           values=<values_array>)

        Required Arguments:
            section = <config_section>
                The name of the config file section, or an empty string for a
                top-level setting.
            key = <key>
                The key portion of a key = value assignment.
            values = <values_array>
                The new values for the key.

        Returns:
            Nothing

        Examples:
            cfg.set_values(section = 'compiler', key = 'debug', 
                           values = ['alpha', 'beta'])
        """
        try :
            if(type(values) != list):
                _utils.exception(msg=f"set_values: values = '{values}' is not a valid list. \n\
                    \rSpecify values in list format, ex. values = ['first_value','second_value']")

            request = config_pb2.SetValuesRequest(path = self.path, section = section, key = key, values = values)
            response = self.config_service.SetValues(request)
            return response

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="set_values failed", ex=e)

    def add_values(self, section = '', key = '', values = []):
        """
        add_values:
            Add more repeated values for the key in a specific section of a
            config file. This will add one key=value assignment for each value.
            Any earlier values for the key will NOT be removed.

        Prototype:
            cfg.add_values(section = <config_section>, key = <key>,
                           values = <string_array>)

        Required Arguments:
            section = <config_section>
                The name of the config file section, or an empty string for a 
                top-level setting.
            key = <key>
                The key portion of a key=value assignment
            values = <string_array>
                The new values for the key.

        Returns:
            Nothing

        Examples:
            cfg.add_values(section='compiler', key='debug', 
                           values=['alpha', 'beta'])
        """
        try :
            if(type(values) != list):
                _utils.exception(msg=f"add_values: values = '{values}' is not a valid list. \n\
                    \rSpecify values in list format, ex. values = ['first_value','second_value']")

            request = config_pb2.AddValuesRequest(path = self.path, section = section, key = key, values = values)
            response = self.config_service.AddValues(request)
            return response

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="add_values failed", ex=e)

    def add_lines(self, section = '', lines = []):
        """
        add_lines:
            Add more assignments in a specific section of a config file.
            This does not ensure uniqueness of the new assignments, and does
            not remove any existing assignments.

        Prototype:
            cfg.add_lines(section = <config_section>, lines = <string_array>)

        Required Arguments:
            section = <config_section>
                The name of the config file section, or an empty string for a 
                top-level setting.
            lines = <string_array>
                The new assignments to add to the section.

        Returns:
            Nothing

        Examples:
            cfg.add_lines(section='compiler', lines=['key1=alpha','key2=beta'])
        """
        try :
            if(type(lines) != list):
                _utils.exception(msg=f"add_lines: lines = '{lines}' is not a valid list. \n\
                    \rSpecify lines in list format, ex. values = ['first_value','second_value']")

            request = config_pb2.AddLinesRequest(path = self.path, section = section, lines = lines)
            response = self.config_service.AddLines(request)
            return response

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="add_lines failed", ex=e)

    def remove(self, section = '', keysOrLines = []):
        """
        remove:
            Remove assignments form a section. The assignments can be identified
            by the key, or the complete assignment.

        Prototype:
            cfg.remove(section=<config_section>, keysOrLines=<string_array>)

        Required Arguments:
            section = <config_section>
                The name of the config file section, or an empty string for a top-level setting.
            keysOrLines = <string_array>
                The list of keys or assignment lines to remove.

        Returns:
            Nothing

        Examples:
            Remove a top-level key:
            cfg.remove(section='compiler', keysOrLines['key1'])

            Remove a single key:
            cfg.remove(section='compiler', keysOrLines['key1'])

            Remove an assignment:
            cfg.remove(section='debug', keysOrLines=['key2=beta'])

            Remove a key and an assignment:
            cfg.remove(section='compiler', keysOrLines=['key1', 'key2=beta'])
        """
        try :
            request = config_pb2.RemoveRequest(path = self.path, section = section, keysOrLines = keysOrLines)
            response = self.config_service.Remove(request)
            return response

        except grpc.RpcError as e:
            _utils.grpc_exception(msg="remove failed", ex=e)


class ConfigFileService(object):
    """
    Client Class for Vitis config file service
    """

    def __init__(self, server):
        self.stub = config_pb2_grpc.ConfigServiceStub(server.channel)

    def __str__(self) -> str:
        data = f""
        return (data)

    def __repr__(self):
        return (self.__str__())

    def config_file(self, path) -> ConfigFile:
        return ConfigFile(self.stub, path);
