import os
import grpc
import socket, errno
import subprocess
import time
import platform
import signal
import re
import json

import workspace_pb2_grpc
import workspace_pb2
from vitis import _utils
from weakref import WeakValueDictionary

class Singleton(type):
    _instances = WeakValueDictionary()
    def __call__(cls, *args, **kwargs):
         if cls not in cls._instances:
            instance = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
         else:
            cls._instances[cls].__init__(*args, **kwargs)

         return cls._instances[cls]

class Server(object, metaclass=Singleton):
    """
    Vitis gRPC Server Client functionality
    """
    #Server Class Member Variables
    #Default settings
    host = None
    cp = None
    workspace = None
    serverPort = None
    channel = None

    def __init__(self, port, host, workspace):

        self.host = host
        if (port != None):
            if (isinstance(port, int) == False):
                if (isinstance(port, str) == False):
                    _utils.exception(msg=f"Expected \"port=<integer or string>\", but got '{port}'", ex_type='ValueError')
                else:
                    try:
                        port = int(port)
                    except ArithmeticError:
                        raise
            if (port < 1024):
                _utils.exception(msg="Port number should be > 1023", ex_type='ValueError')
            self.serverPort = port

        self.workspace = workspace

        try:
            if self.verify() != True:
                try:
                    if (self.startServer()):
                        if (self.serverPort != None):
                            if (self.host == "localhost"):
                                print(f"Vitis Server started on port '{self.serverPort}'.")
                            else :
                                print(f"Vitis Server started on host \'{self.host}\', port \'{self.serverPort}\'.")
                        else:
                            _utils.exception(msg="Failed to start Vitis Server")
                    else:
                        _utils.exception(msg=f"Failed to find free port on host '{self.host}' to start Vitis Server")

                except OSError as e:
                    if e.errno != errno.EEXIST:
                        _utils.exception(msg="Error while starting server", ex=e)
                except grpc.RpcError as e :
                    _utils.grpc_exception(msg="Failed to start the Vitis Server", ex=e)
            else :
                if (self.host == "localhost"):
                     print(f"Vitis client connected to server already running on port '{self.serverPort}'.")
                else :
                     print(f"Vitis client connected to server already running on host \'{self.host}\', port \'{self.serverPort}\'.")


            self.createChannel(self.host, self.serverPort)
            self.initWorkspaceStub(self.workspace)

        except socket.error as e:
             if e.errno == errno.EADDRINUSE:
                _utils.exception(msg=f"Port '{port}' is already in use", ex=e)

    # def get_free_tcp_port(self, host) : Method removed to find free port on the server itself

    def createChannel(self, host, port):
        #Start gRPC channel
        try:
            self.channel = grpc.insecure_channel(
                '{}:{}'.format(host, port))
            try:
                timeout = int(os.getenv("VITIS_SERVER_START_TIMEOUT", "60"))
                grpc.channel_ready_future(self.channel).result(timeout)
                return True
            except grpc.FutureTimeoutError:
                exp_msg = "Timeout while connecting to Vitis Server, "
                exp_msg = exp_msg + str(self.cp.stdout.read(), 'utf-8')
                _utils.exception(msg=exp_msg)
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Failed to create Vitis gRPC secure channel", ex=e)
        except grpc._channel._InactiveRpcError as e:
            _utils.exception(msg="Vitis gRPC secure channel is inactive", ex=e)

    def startServer(self):
        xilinxVitisEnv = os.getenv("XILINX_VITIS")
        serverBinFile=""
        try:
            if (xilinxVitisEnv != None) :
                serverBinFile = xilinxVitisEnv + "/bin/vitis-server"
            else:
                DIR = os.path.dirname(os.path.abspath(__file__))
                serverBinFile = DIR + "/../../rigel-server/build/install/rigel-server/bin/vitisng-server"

            if (platform.system() == "Windows"):
                serverBinFile +=".bat"
            if (os.path.exists(serverBinFile)):
                serverCmd = os.path.abspath(serverBinFile)
                # Starting the server with mentioned port
                if(self.serverPort != None):
                    serverCmd += " -p " + str(self.serverPort)

                if (platform.system() == "Windows"):
                    self.cp = subprocess.Popen(serverCmd, shell = True, start_new_session=True, 
                                            stdout = subprocess.PIPE, stderr =  subprocess.STDOUT, 
                                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                else:
                    self.cp = subprocess.Popen(serverCmd, shell = True, start_new_session=True, stdout = subprocess.PIPE, stderr =  subprocess.STDOUT)
                # Read port from the server log
                if(self.serverPort==None):
                    for line in iter(self.cp.stdout.readline,''):
                        line = str(line, 'utf-8')
                        if("serverPort" in line):
                            line = re.split("\{(.*?)\}", line)[1]
                            line = json.loads('{'+line+'}')
                            self.serverPort = int(line['serverPort'])
                            break
                return True
            else:
                _utils.exception(msg=f"Unable to start Vitis Server, cannot find '{serverBinFile}'")
        finally:
            pass

    def verify(self):
        if self.channel == None:
            return False
        try:
            grpc.channel_ready_future(self.channel).result(0.1)
            return True
        except grpc.FutureTimeoutError:
            return False

    #Internal method
    def restart(self):
        if (self.verify() != True):
            try:
                self.startServer()
                self.createChannel(self.host, self.serverPort)
            except OSError as e:
                    if e.errno != errno.EEXIST:
                        _utils.exception(msg="Error while starting server", ex=e)
            except grpc.RpcError as e :
                    _utils.grpc_exception(msg=f"Failed to start the Vitis Server", ex=e)
        else:
            print(f"Vitis Server already running on port {self.serverPort}.")

    def stop(self):
        if self.cp:
            #TODO: Fix for CR-1136659
            # "Exception in thread Thread-1:" error observed in Linux console when running simple vitis cli tests
            time.sleep(0.2)
            print(f"Shutting down Vitis server running on port '{self.serverPort}'")
            self.channel.close()
            #  self.cp.terminate()
            if (platform.system() == "Windows"):
                self.cp.kill()
            else:
                os.killpg(os.getpgid(self.cp.pid), signal.SIGTERM)
            self.cp = None
            self.serverPort = None
            self.host = None
            self.workspace = None
            self.channel = None

    def initWorkspaceStub(self, path):
        try:
            self.stubWs  = workspace_pb2_grpc.WorkspaceServiceStub(self.channel)
            if (path != None):
                self.setWorkspace(path)
        except OSError as e:
            _utils.exception(msg="Workspace service initiation failed", ex=e)

    def setWorkspace(self, path):
        try:
            absPath = os.path.abspath(path)
            wsRequest  =  workspace_pb2.Workspace(path=absPath)
            response  = self.stubWs.SetWorkspace(wsRequest)

            return response.status
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot set workspace", ex=e)

    def getWorkspace(self, func="get_workspace"):
        try:
            getWsRequest  =  workspace_pb2.GetWorkspaceRequest(name="")
            response  = self.stubWs.GetWorkspace(getWsRequest)
            return response.path
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot get workspace", ex=e)

    def checkWorkspaceSet(self):
        try:
            checkWsRequest  =  workspace_pb2.CheckWorkspaceRequest(name="")
            response  = self.stubWs.checkWorkspaceSet(checkWsRequest)
            return response.status
        except grpc.RpcError as e:
            # TODO: better error message
            _utils.grpc_exception(msg="check_workspace failed", ex=e)
