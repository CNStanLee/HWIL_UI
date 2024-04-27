import grpc
import build_pb2_grpc
import build_pb2
from vitis import _utils

class Build(object):
    """
    Client Class for Build service.
    """

    def __init__(self, server):
        
        self._server = server
        self.stub = build_pb2_grpc.BuildServiceStub(self._server.channel)

    def generateBuildFiles(self, name):
        try:
            workspace = self._server.getWorkspace(func="generate_build_files")
            if (workspace == None):
                return
            buildRequest =  build_pb2.BuildRequest(app_name=name,
                                                   serial_build = False,
                                                   app_parent_path=workspace)

            self.stub.GenerateBuildFiles(buildRequest)

            return True
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot generate build files for '{name}'", ex=e)

    #Internal method
    def listRunningBuilds(self):
        try:
            listBuildsRequest =  build_pb2.ListRunningBuildsRequest()
            runningBuilds = self.stub.ListRunningBuilds(listBuildsRequest)

            listRunningBuilds = list()
            for runningBuild in runningBuilds.running_builds:
                buildDict = dict()
                buildDict['app_path'] = runningBuild.app_path
                buildDict['component_name'] = runningBuild.component_name
                buildDict['build_cfg'] = runningBuild.build_cfg
                listRunningBuilds.append(buildDict)

            return listRunningBuilds
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot list running builds", ex=e)

    def build_app(self, name, comp_name, target, build_comps):

        try:
            workspace = self._server.getWorkspace(func="build_app")
            if (workspace == None):
                return

            buildRequest =  build_pb2.BuildRequest(app_name=name,
                                                   build_cfg=target,
                                                   build_target='all',
                                                   component_name=comp_name,
                                                   serial_build = False,
                                                   app_parent_path=workspace,
                                                   build_comps = build_comps)

            buildResponse = self.stub.Build(buildRequest)

            retStatus = None
            for buildStream in buildResponse:
                retStatus = buildStream.type
                for logLine in buildStream.log:
                     print(logLine)

            return retStatus
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot build app '{name}'", ex=e)

    #Internal method
    def cancel_build(self, app_path, component_name, build_cfg):

        try:
            workspace = self._server.getWorkspace(func="cancel_build")
            if (workspace == None):
                return

            runningBuild =  build_pb2.RunningBuild(app_path=app_path,
                                                   component_name=component_name,
                                                   build_cfg=build_cfg)

            self.stub.CancelRunningBuild(runningBuild)

            retStatus = None
            return retStatus
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot cancel running build '{app_path}'", ex=e)

    def clean_app(self, name, target, comp_name, build_target="clean"):

        try:
            workspace = self._server.getWorkspace(func="clean_app")
            if (workspace == None):
                return

            buildRequest =  build_pb2.BuildRequest(app_name=name,
                                                   component_name = comp_name,
                                                   build_cfg = target,
                                                   app_parent_path = workspace,
                                                   serial_build = True,
                                                   build_target = build_target)

            buildResponse = self.stub.Build(buildRequest)

            retStatus = None
            for buildStream in buildResponse:
                retStatus = buildStream.type
                for logLine in buildStream.log:
                     print(logLine)

            return retStatus
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot clean app '{name}'", ex=e)

# Component build and clean

    def build_comp(self, name, type, target):
        try:
            workspace = self._server.getWorkspace(func="comp")
            if (workspace == None):
                return

            buildRequest =  build_pb2.BuildRequest(app_name=name,
                                                build_cfg=target,
                                                build_target='all',
                                                type = type,
                                                serial_build = True,
                                                app_parent_path=workspace)

            buildResponse = self.stub.Build(buildRequest)

            retStatus = None
            for buildStream in buildResponse:
                retStatus = buildStream.type
                for logLine in buildStream.log:
                    print(logLine)

            return retStatus
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot build component '{name}'", ex=e)

    def clean_comp(self, name, type, target):
        try:
            workspace = self._server.getWorkspace(func="clean_comp")
            if (workspace == None):
                return

            buildRequest =  build_pb2.BuildRequest(app_name=name,
                                                   build_cfg=target,
                                                   type = type,
                                                   build_target="clean",
                                                   app_parent_path=workspace,
                                                   serial_build = True,
                                                   )

            buildResponse = self.stub.Build(buildRequest)

            retStatus = None
            for buildStream in buildResponse:
                retStatus = buildStream.type
                for logLine in buildStream.log:
                    print(logLine)

            return retStatus
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot clean component '{name}'", ex=e)
            
            
    def getAppConfig(self, component_location):
        try:
            buildSettingsRequest =  build_pb2.BuildSettingsRequest(
                                component_location = component_location,
                                requestType = build_pb2.BuildSettingsRequest.RequestType.READ)

            buildResponse = self.stub.ReadCMakeBuildSettings(buildSettingsRequest)

            return buildResponse
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Unable to get the build configuration'", ex=e)
            
    def setAppConfig(self, component_location, key, values):
        try:
            cmake_setting = build_pb2.CMakeBuildSetting(key = key, value = values)
            buildSettingsRequest =  build_pb2.BuildSettingsRequest(
                                component_location = component_location,
                                requestType = build_pb2.BuildSettingsRequest.RequestType.WRITE,
                                settings = [cmake_setting])

            self.stub.WriteCMakeBuildSettings(buildSettingsRequest)
            return
        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Unable to get the build configuration'", ex=e)
