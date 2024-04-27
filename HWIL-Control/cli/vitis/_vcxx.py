from typing import Callable, Optional
from weakref import WeakValueDictionary
import grpc
import vcxx_pb2
import vcxx_pb2_grpc
from vitis import _utils


class Singleton(type):
    _instances = WeakValueDictionary()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance

        return cls._instances[cls]

class Vcxx(object, metaclass=Singleton):
    """
    Client class for Vitis C++ service.
    """

    def __init__(self, serverObj):
        self._server = serverObj
        self._stub = vcxx_pb2_grpc.VcxxServiceStub(self._server.channel)

    def has_vcxx(self) -> bool:
        """
        Check whether the Vitis C++ service is available.

        Returns:
            True if Vitis C++ service available, False if not.
        """
        try:
            req = vcxx_pb2.HasVcxxRequest()
            resp = self._stub.hasVcxx(req)
            return resp.hasVcxx

        except grpc.RpcError as e:
            _utils.grpc_exception(
                msg=f"Cannot determine availability of Vitis C++ service",
                ex=e)

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
        try:
            req = vcxx_pb2.CallVcxxRequest(
                methodAndParams=vcxx_pb2.CallVcxxMethodAndParams(
                    methodName=method_name, paramsJson=params_json))
            result_json = 'null'
            for resp in self._stub.callVcxx(iter([req])):
                if resp.HasField('error'):
                    err = resp.error
                    _utils.exception(
                        msg=f'Vitis C++ call {repr(method_name):s} failed:'
                        f' {err.message:s} (code {err.code:d},'
                        f' {repr(err.dataJson):s})')
                if resp.HasField('logMessage'):
                    log_msg = resp.logMessage
                    if log_callback is not None:
                        log_callback(log_msg.level, log_msg.message)
                    continue
                if resp.HasField('resultJson'):
                    result_json = resp.resultJson
            return result_json

        except grpc.RpcError as e:
            _utils.grpc_exception(msg=f"Cannot call Vitis C++ service", ex=e)
