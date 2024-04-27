# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import logger_pb2 as logger__pb2


class LoggerServiceStub(object):
    """This Service is used to enable from clients
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Log = channel.unary_unary(
                '/com.xilinx.rigel.logger.v1.LoggerService/Log',
                request_serializer=logger__pb2.LogRequest.SerializeToString,
                response_deserializer=logger__pb2.LogResponse.FromString,
                )
        self.UpdateLogLevel = channel.unary_unary(
                '/com.xilinx.rigel.logger.v1.LoggerService/UpdateLogLevel',
                request_serializer=logger__pb2.LogLevelRequest.SerializeToString,
                response_deserializer=logger__pb2.LogResponse.FromString,
                )
        self.GetLogLevels = channel.unary_unary(
                '/com.xilinx.rigel.logger.v1.LoggerService/GetLogLevels',
                request_serializer=logger__pb2.LogLevelsRequest.SerializeToString,
                response_deserializer=logger__pb2.LogLevelsResponse.FromString,
                )


class LoggerServiceServicer(object):
    """This Service is used to enable from clients
    """

    def Log(self, request, context):
        """Log message into generic logger
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateLogLevel(self, request, context):
        """Updating Log Level
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetLogLevels(self, request, context):
        """Updating Log Level
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_LoggerServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Log': grpc.unary_unary_rpc_method_handler(
                    servicer.Log,
                    request_deserializer=logger__pb2.LogRequest.FromString,
                    response_serializer=logger__pb2.LogResponse.SerializeToString,
            ),
            'UpdateLogLevel': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateLogLevel,
                    request_deserializer=logger__pb2.LogLevelRequest.FromString,
                    response_serializer=logger__pb2.LogResponse.SerializeToString,
            ),
            'GetLogLevels': grpc.unary_unary_rpc_method_handler(
                    servicer.GetLogLevels,
                    request_deserializer=logger__pb2.LogLevelsRequest.FromString,
                    response_serializer=logger__pb2.LogLevelsResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'com.xilinx.rigel.logger.v1.LoggerService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class LoggerService(object):
    """This Service is used to enable from clients
    """

    @staticmethod
    def Log(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/com.xilinx.rigel.logger.v1.LoggerService/Log',
            logger__pb2.LogRequest.SerializeToString,
            logger__pb2.LogResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateLogLevel(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/com.xilinx.rigel.logger.v1.LoggerService/UpdateLogLevel',
            logger__pb2.LogLevelRequest.SerializeToString,
            logger__pb2.LogResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetLogLevels(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/com.xilinx.rigel.logger.v1.LoggerService/GetLogLevels',
            logger__pb2.LogLevelsRequest.SerializeToString,
            logger__pb2.LogLevelsResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
