# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
import hls_flow_pb2 as hls__flow__pb2


class HLSFlowStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.runOperation = channel.unary_stream(
                '/xilinx.rigel.hls.flow.HLSFlow/runOperation',
                request_serializer=hls__flow__pb2.OperationRequest.SerializeToString,
                response_deserializer=hls__flow__pb2.OperationResponse.FromString,
                )
        self.cancelOperation = channel.unary_unary(
                '/xilinx.rigel.hls.flow.HLSFlow/cancelOperation',
                request_serializer=hls__flow__pb2.OperationRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class HLSFlowServicer(object):
    """Missing associated documentation comment in .proto file."""

    def runOperation(self, request, context):
        """runs a specified operation/action on an HLS component
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def cancelOperation(self, request, context):
        """cancels a running operation/action on an HLS component
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_HLSFlowServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'runOperation': grpc.unary_stream_rpc_method_handler(
                    servicer.runOperation,
                    request_deserializer=hls__flow__pb2.OperationRequest.FromString,
                    response_serializer=hls__flow__pb2.OperationResponse.SerializeToString,
            ),
            'cancelOperation': grpc.unary_unary_rpc_method_handler(
                    servicer.cancelOperation,
                    request_deserializer=hls__flow__pb2.OperationRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'xilinx.rigel.hls.flow.HLSFlow', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class HLSFlow(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def runOperation(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/xilinx.rigel.hls.flow.HLSFlow/runOperation',
            hls__flow__pb2.OperationRequest.SerializeToString,
            hls__flow__pb2.OperationResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def cancelOperation(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/xilinx.rigel.hls.flow.HLSFlow/cancelOperation',
            hls__flow__pb2.OperationRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)