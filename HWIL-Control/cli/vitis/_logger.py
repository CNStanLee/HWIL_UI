import grpc
import logger_pb2_grpc
import logger_pb2
from vitis import _utils

# TODO: get this list from server
logLevels = ['OFF', 'FATAL', 'ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE', 'ALL']


class Logger(object):
    """
    Client Class for Logger service.
    """

    def __init__(self, server):

        self._server = server
        self.stub = logger_pb2_grpc.LoggerServiceStub(self._server.channel)

    def log_level(self, log_level=None):
        global logLevels

        if (log_level == None):
            # TODO: return the current level when its supported by Logger service
            _utils.exception(msg=f"Log level must be specified. Valid log levels are\n\
                \r'{logLevels}'")

        if (log_level not in logLevels):
            _utils.exception(msg=f"Invalid log level '{log_level}'. Valid log levels are\n\
                \r'{logLevels}'")
        try:
            loggerRequest =  logger_pb2.LogLevelRequest(level = log_level.upper())
            loggerResponse = self.stub.UpdateLogLevel(loggerRequest)

            return loggerResponse.success
        except grpc.RpcError as e:
            _utils.grpc_exception(msg="Cannot set log level", ex=e)
