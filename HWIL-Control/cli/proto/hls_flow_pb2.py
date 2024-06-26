# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: hls_flow.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='hls_flow.proto',
  package='xilinx.rigel.hls.flow',
  syntax='proto3',
  serialized_options=b'\n#com.xilinx.hls.server.proto.hlsFlowB\014HlsFlowProtoP\001',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0ehls_flow.proto\x12\x15xilinx.rigel.hls.flow\x1a\x1bgoogle/protobuf/empty.proto\"l\n\x10OperationRequest\x12\x1a\n\x12\x63omponent_location\x18\x01 \x01(\t\x12<\n\x0eoperation_type\x18\x02 \x01(\x0e\x32$.xilinx.rigel.hls.flow.OperationType\"S\n\x11OperationResponse\x12\x31\n\x06status\x18\x01 \x01(\x0e\x32!.xilinx.rigel.hls.flow.StatusType\x12\x0b\n\x03log\x18\x02 \x03(\t*\x97\x01\n\rOperationType\x12\x10\n\x0c\x43_SIMULATION\x10\x00\x12\r\n\tSYNTHESIS\x10\x01\x12\x11\n\rCO_SIMULATION\x10\x02\x12\x12\n\x0eIMPLEMENTATION\x10\x03\x12\x19\n\x15\x41NALYSIS_OPTIMIZATION\x10\x04\x12\x0b\n\x07PACKAGE\x10\x05\x12\x16\n\x12\x43_SIMULATION_DEBUG\x10\x06*D\n\nStatusType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x0f\n\x0bIN_PROGRESS\x10\x01\x12\x0b\n\x07SUCCESS\x10\x02\x12\x0b\n\x07\x46\x41ILURE\x10\x03\x32\xc6\x01\n\x07HLSFlow\x12\x65\n\x0crunOperation\x12\'.xilinx.rigel.hls.flow.OperationRequest\x1a(.xilinx.rigel.hls.flow.OperationResponse\"\x00\x30\x01\x12T\n\x0f\x63\x61ncelOperation\x12\'.xilinx.rigel.hls.flow.OperationRequest\x1a\x16.google.protobuf.Empty\"\x00\x42\x35\n#com.xilinx.hls.server.proto.hlsFlowB\x0cHlsFlowProtoP\x01\x62\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,])

_OPERATIONTYPE = _descriptor.EnumDescriptor(
  name='OperationType',
  full_name='xilinx.rigel.hls.flow.OperationType',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='C_SIMULATION', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SYNTHESIS', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CO_SIMULATION', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='IMPLEMENTATION', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='ANALYSIS_OPTIMIZATION', index=4, number=4,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='PACKAGE', index=5, number=5,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='C_SIMULATION_DEBUG', index=6, number=6,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=266,
  serialized_end=417,
)
_sym_db.RegisterEnumDescriptor(_OPERATIONTYPE)

OperationType = enum_type_wrapper.EnumTypeWrapper(_OPERATIONTYPE)
_STATUSTYPE = _descriptor.EnumDescriptor(
  name='StatusType',
  full_name='xilinx.rigel.hls.flow.StatusType',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='IN_PROGRESS', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SUCCESS', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FAILURE', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=419,
  serialized_end=487,
)
_sym_db.RegisterEnumDescriptor(_STATUSTYPE)

StatusType = enum_type_wrapper.EnumTypeWrapper(_STATUSTYPE)
C_SIMULATION = 0
SYNTHESIS = 1
CO_SIMULATION = 2
IMPLEMENTATION = 3
ANALYSIS_OPTIMIZATION = 4
PACKAGE = 5
C_SIMULATION_DEBUG = 6
UNKNOWN = 0
IN_PROGRESS = 1
SUCCESS = 2
FAILURE = 3



_OPERATIONREQUEST = _descriptor.Descriptor(
  name='OperationRequest',
  full_name='xilinx.rigel.hls.flow.OperationRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='component_location', full_name='xilinx.rigel.hls.flow.OperationRequest.component_location', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='operation_type', full_name='xilinx.rigel.hls.flow.OperationRequest.operation_type', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=70,
  serialized_end=178,
)


_OPERATIONRESPONSE = _descriptor.Descriptor(
  name='OperationResponse',
  full_name='xilinx.rigel.hls.flow.OperationResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='xilinx.rigel.hls.flow.OperationResponse.status', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='log', full_name='xilinx.rigel.hls.flow.OperationResponse.log', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=180,
  serialized_end=263,
)

_OPERATIONREQUEST.fields_by_name['operation_type'].enum_type = _OPERATIONTYPE
_OPERATIONRESPONSE.fields_by_name['status'].enum_type = _STATUSTYPE
DESCRIPTOR.message_types_by_name['OperationRequest'] = _OPERATIONREQUEST
DESCRIPTOR.message_types_by_name['OperationResponse'] = _OPERATIONRESPONSE
DESCRIPTOR.enum_types_by_name['OperationType'] = _OPERATIONTYPE
DESCRIPTOR.enum_types_by_name['StatusType'] = _STATUSTYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

OperationRequest = _reflection.GeneratedProtocolMessageType('OperationRequest', (_message.Message,), {
  'DESCRIPTOR' : _OPERATIONREQUEST,
  '__module__' : 'hls_flow_pb2'
  # @@protoc_insertion_point(class_scope:xilinx.rigel.hls.flow.OperationRequest)
  })
_sym_db.RegisterMessage(OperationRequest)

OperationResponse = _reflection.GeneratedProtocolMessageType('OperationResponse', (_message.Message,), {
  'DESCRIPTOR' : _OPERATIONRESPONSE,
  '__module__' : 'hls_flow_pb2'
  # @@protoc_insertion_point(class_scope:xilinx.rigel.hls.flow.OperationResponse)
  })
_sym_db.RegisterMessage(OperationResponse)


DESCRIPTOR._options = None

_HLSFLOW = _descriptor.ServiceDescriptor(
  name='HLSFlow',
  full_name='xilinx.rigel.hls.flow.HLSFlow',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=490,
  serialized_end=688,
  methods=[
  _descriptor.MethodDescriptor(
    name='runOperation',
    full_name='xilinx.rigel.hls.flow.HLSFlow.runOperation',
    index=0,
    containing_service=None,
    input_type=_OPERATIONREQUEST,
    output_type=_OPERATIONRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='cancelOperation',
    full_name='xilinx.rigel.hls.flow.HLSFlow.cancelOperation',
    index=1,
    containing_service=None,
    input_type=_OPERATIONREQUEST,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_HLSFLOW)

DESCRIPTOR.services_by_name['HLSFlow'] = _HLSFLOW

# @@protoc_insertion_point(module_scope)
