# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: profiledata.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import aie_pb2 as aie__pb2
import basicreport_pb2 as basicreport__pb2
import systemdiag_pb2 as systemdiag__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='profiledata.proto',
  package='xilinx.rigel.profile.v1',
  syntax='proto3',
  serialized_options=b'\n\033com.xilinx.rigel.profile.v1P\001',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x11profiledata.proto\x12\x17xilinx.rigel.profile.v1\x1a\taie.proto\x1a\x11\x62\x61sicreport.proto\x1a\x10systemdiag.proto\"\xff\x01\n\x0fProfileSumModel\x12\x32\n\x04tree\x18\x01 \x01(\x0b\x32$.xilinx.rigel.basicreport.v1.NavTree\x12M\n\x0bsection_map\x18\x02 \x03(\x0b\x32\x38.xilinx.rigel.profile.v1.ProfileSumModel.SectionMapEntry\x12\x14\n\x0c\x63ommand_line\x18\x03 \x01(\t\x1aS\n\x0fSectionMapEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12/\n\x05value\x18\x02 \x01(\x0b\x32 .xilinx.rigel.profile.v1.Section:\x02\x38\x01\"\xf4\x01\n\x07Section\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0b\n\x03key\x18\x02 \x01(\t\x12>\n\x0bno_contents\x18\x03 \x01(\x0b\x32\'.xilinx.rigel.basicreport.v1.NoContentsH\x00\x12\x44\n\x0e\x62\x61sic_contents\x18\x04 \x01(\x0b\x32*.xilinx.rigel.basicreport.v1.BasicContentsH\x00\x12<\n\x0c\x61ie_contents\x18\x05 \x01(\x0b\x32$.xilinx.rigel.profile.v1.AieContentsH\x00\x42\n\n\x08\x63ontents\"F\n\x10ProfileTreeModel\x12\x32\n\x08sections\x18\x01 \x03(\x0b\x32 .xilinx.rigel.profile.v1.Section\"\xcb\x01\n\x0b\x41ieContents\x12?\n\x11\x61ie_metrics_model\x18\x01 \x01(\x0b\x32$.xilinx.rigel.aie.v1.AieMetricsModel\x12;\n\taie_table\x18\x03 \x01(\x0b\x32(.xilinx.rigel.profile.v1.AieProfileTable\x12>\n\x0f\x61ie_line_graphs\x18\x02 \x03(\x0b\x32%.xilinx.rigel.profile.v1.AieLineGraph\"\x82\x02\n\x0f\x41ieProfileTable\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x46\n\x10metric_col_specs\x18\x02 \x03(\x0b\x32,.xilinx.rigel.aie.v1.AieTileMetricColumnSpec\x12H\n\x11metric_col_groups\x18\x03 \x03(\x0b\x32-.xilinx.rigel.aie.v1.AieTileMetricColumnGroup\x12\x39\n\x04rows\x18\x04 \x03(\x0b\x32+.xilinx.rigel.profile.v1.AieProfileTableRow\x12\x14\n\x0cshow_percent\x18\x05 \x01(\x08\"\x93\x01\n\x12\x41ieProfileTableRow\x12\x36\n\nselectable\x18\x01 \x01(\x0b\x32\".xilinx.rigel.aie.v1.AieSelectable\x12\x15\n\rshow_in_chart\x18\x02 \x01(\x08\x12\x15\n\rmetric_values\x18\x03 \x03(\t\x12\x17\n\x0fmetric_percents\x18\x04 \x03(\t\":\n\x0c\x41ieLineGraph\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0b\n\x03key\x18\x02 \x01(\t\x12\x0f\n\x07\x65ntries\x18\x04 \x03(\tB\x1f\n\x1b\x63om.xilinx.rigel.profile.v1P\x01\x62\x06proto3'
  ,
  dependencies=[aie__pb2.DESCRIPTOR,basicreport__pb2.DESCRIPTOR,systemdiag__pb2.DESCRIPTOR,])




_PROFILESUMMODEL_SECTIONMAPENTRY = _descriptor.Descriptor(
  name='SectionMapEntry',
  full_name='xilinx.rigel.profile.v1.ProfileSumModel.SectionMapEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='xilinx.rigel.profile.v1.ProfileSumModel.SectionMapEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='xilinx.rigel.profile.v1.ProfileSumModel.SectionMapEntry.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=267,
  serialized_end=350,
)

_PROFILESUMMODEL = _descriptor.Descriptor(
  name='ProfileSumModel',
  full_name='xilinx.rigel.profile.v1.ProfileSumModel',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='tree', full_name='xilinx.rigel.profile.v1.ProfileSumModel.tree', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='section_map', full_name='xilinx.rigel.profile.v1.ProfileSumModel.section_map', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='command_line', full_name='xilinx.rigel.profile.v1.ProfileSumModel.command_line', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_PROFILESUMMODEL_SECTIONMAPENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=95,
  serialized_end=350,
)


_SECTION = _descriptor.Descriptor(
  name='Section',
  full_name='xilinx.rigel.profile.v1.Section',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='xilinx.rigel.profile.v1.Section.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='key', full_name='xilinx.rigel.profile.v1.Section.key', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='no_contents', full_name='xilinx.rigel.profile.v1.Section.no_contents', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='basic_contents', full_name='xilinx.rigel.profile.v1.Section.basic_contents', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='aie_contents', full_name='xilinx.rigel.profile.v1.Section.aie_contents', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
    _descriptor.OneofDescriptor(
      name='contents', full_name='xilinx.rigel.profile.v1.Section.contents',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=353,
  serialized_end=597,
)


_PROFILETREEMODEL = _descriptor.Descriptor(
  name='ProfileTreeModel',
  full_name='xilinx.rigel.profile.v1.ProfileTreeModel',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='sections', full_name='xilinx.rigel.profile.v1.ProfileTreeModel.sections', index=0,
      number=1, type=11, cpp_type=10, label=3,
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
  serialized_start=599,
  serialized_end=669,
)


_AIECONTENTS = _descriptor.Descriptor(
  name='AieContents',
  full_name='xilinx.rigel.profile.v1.AieContents',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='aie_metrics_model', full_name='xilinx.rigel.profile.v1.AieContents.aie_metrics_model', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='aie_table', full_name='xilinx.rigel.profile.v1.AieContents.aie_table', index=1,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='aie_line_graphs', full_name='xilinx.rigel.profile.v1.AieContents.aie_line_graphs', index=2,
      number=2, type=11, cpp_type=10, label=3,
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
  serialized_start=672,
  serialized_end=875,
)


_AIEPROFILETABLE = _descriptor.Descriptor(
  name='AieProfileTable',
  full_name='xilinx.rigel.profile.v1.AieProfileTable',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='xilinx.rigel.profile.v1.AieProfileTable.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='metric_col_specs', full_name='xilinx.rigel.profile.v1.AieProfileTable.metric_col_specs', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='metric_col_groups', full_name='xilinx.rigel.profile.v1.AieProfileTable.metric_col_groups', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='rows', full_name='xilinx.rigel.profile.v1.AieProfileTable.rows', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='show_percent', full_name='xilinx.rigel.profile.v1.AieProfileTable.show_percent', index=4,
      number=5, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
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
  serialized_start=878,
  serialized_end=1136,
)


_AIEPROFILETABLEROW = _descriptor.Descriptor(
  name='AieProfileTableRow',
  full_name='xilinx.rigel.profile.v1.AieProfileTableRow',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='selectable', full_name='xilinx.rigel.profile.v1.AieProfileTableRow.selectable', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='show_in_chart', full_name='xilinx.rigel.profile.v1.AieProfileTableRow.show_in_chart', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='metric_values', full_name='xilinx.rigel.profile.v1.AieProfileTableRow.metric_values', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='metric_percents', full_name='xilinx.rigel.profile.v1.AieProfileTableRow.metric_percents', index=3,
      number=4, type=9, cpp_type=9, label=3,
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
  serialized_start=1139,
  serialized_end=1286,
)


_AIELINEGRAPH = _descriptor.Descriptor(
  name='AieLineGraph',
  full_name='xilinx.rigel.profile.v1.AieLineGraph',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='xilinx.rigel.profile.v1.AieLineGraph.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='key', full_name='xilinx.rigel.profile.v1.AieLineGraph.key', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='entries', full_name='xilinx.rigel.profile.v1.AieLineGraph.entries', index=2,
      number=4, type=9, cpp_type=9, label=3,
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
  serialized_start=1288,
  serialized_end=1346,
)

_PROFILESUMMODEL_SECTIONMAPENTRY.fields_by_name['value'].message_type = _SECTION
_PROFILESUMMODEL_SECTIONMAPENTRY.containing_type = _PROFILESUMMODEL
_PROFILESUMMODEL.fields_by_name['tree'].message_type = basicreport__pb2._NAVTREE
_PROFILESUMMODEL.fields_by_name['section_map'].message_type = _PROFILESUMMODEL_SECTIONMAPENTRY
_SECTION.fields_by_name['no_contents'].message_type = basicreport__pb2._NOCONTENTS
_SECTION.fields_by_name['basic_contents'].message_type = basicreport__pb2._BASICCONTENTS
_SECTION.fields_by_name['aie_contents'].message_type = _AIECONTENTS
_SECTION.oneofs_by_name['contents'].fields.append(
  _SECTION.fields_by_name['no_contents'])
_SECTION.fields_by_name['no_contents'].containing_oneof = _SECTION.oneofs_by_name['contents']
_SECTION.oneofs_by_name['contents'].fields.append(
  _SECTION.fields_by_name['basic_contents'])
_SECTION.fields_by_name['basic_contents'].containing_oneof = _SECTION.oneofs_by_name['contents']
_SECTION.oneofs_by_name['contents'].fields.append(
  _SECTION.fields_by_name['aie_contents'])
_SECTION.fields_by_name['aie_contents'].containing_oneof = _SECTION.oneofs_by_name['contents']
_PROFILETREEMODEL.fields_by_name['sections'].message_type = _SECTION
_AIECONTENTS.fields_by_name['aie_metrics_model'].message_type = aie__pb2._AIEMETRICSMODEL
_AIECONTENTS.fields_by_name['aie_table'].message_type = _AIEPROFILETABLE
_AIECONTENTS.fields_by_name['aie_line_graphs'].message_type = _AIELINEGRAPH
_AIEPROFILETABLE.fields_by_name['metric_col_specs'].message_type = aie__pb2._AIETILEMETRICCOLUMNSPEC
_AIEPROFILETABLE.fields_by_name['metric_col_groups'].message_type = aie__pb2._AIETILEMETRICCOLUMNGROUP
_AIEPROFILETABLE.fields_by_name['rows'].message_type = _AIEPROFILETABLEROW
_AIEPROFILETABLEROW.fields_by_name['selectable'].message_type = aie__pb2._AIESELECTABLE
DESCRIPTOR.message_types_by_name['ProfileSumModel'] = _PROFILESUMMODEL
DESCRIPTOR.message_types_by_name['Section'] = _SECTION
DESCRIPTOR.message_types_by_name['ProfileTreeModel'] = _PROFILETREEMODEL
DESCRIPTOR.message_types_by_name['AieContents'] = _AIECONTENTS
DESCRIPTOR.message_types_by_name['AieProfileTable'] = _AIEPROFILETABLE
DESCRIPTOR.message_types_by_name['AieProfileTableRow'] = _AIEPROFILETABLEROW
DESCRIPTOR.message_types_by_name['AieLineGraph'] = _AIELINEGRAPH
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ProfileSumModel = _reflection.GeneratedProtocolMessageType('ProfileSumModel', (_message.Message,), {

  'SectionMapEntry' : _reflection.GeneratedProtocolMessageType('SectionMapEntry', (_message.Message,), {
    'DESCRIPTOR' : _PROFILESUMMODEL_SECTIONMAPENTRY,
    '__module__' : 'profiledata_pb2'
    # @@protoc_insertion_point(class_scope:xilinx.rigel.profile.v1.ProfileSumModel.SectionMapEntry)
    })
  ,
  'DESCRIPTOR' : _PROFILESUMMODEL,
  '__module__' : 'profiledata_pb2'
  # @@protoc_insertion_point(class_scope:xilinx.rigel.profile.v1.ProfileSumModel)
  })
_sym_db.RegisterMessage(ProfileSumModel)
_sym_db.RegisterMessage(ProfileSumModel.SectionMapEntry)

Section = _reflection.GeneratedProtocolMessageType('Section', (_message.Message,), {
  'DESCRIPTOR' : _SECTION,
  '__module__' : 'profiledata_pb2'
  # @@protoc_insertion_point(class_scope:xilinx.rigel.profile.v1.Section)
  })
_sym_db.RegisterMessage(Section)

ProfileTreeModel = _reflection.GeneratedProtocolMessageType('ProfileTreeModel', (_message.Message,), {
  'DESCRIPTOR' : _PROFILETREEMODEL,
  '__module__' : 'profiledata_pb2'
  # @@protoc_insertion_point(class_scope:xilinx.rigel.profile.v1.ProfileTreeModel)
  })
_sym_db.RegisterMessage(ProfileTreeModel)

AieContents = _reflection.GeneratedProtocolMessageType('AieContents', (_message.Message,), {
  'DESCRIPTOR' : _AIECONTENTS,
  '__module__' : 'profiledata_pb2'
  # @@protoc_insertion_point(class_scope:xilinx.rigel.profile.v1.AieContents)
  })
_sym_db.RegisterMessage(AieContents)

AieProfileTable = _reflection.GeneratedProtocolMessageType('AieProfileTable', (_message.Message,), {
  'DESCRIPTOR' : _AIEPROFILETABLE,
  '__module__' : 'profiledata_pb2'
  # @@protoc_insertion_point(class_scope:xilinx.rigel.profile.v1.AieProfileTable)
  })
_sym_db.RegisterMessage(AieProfileTable)

AieProfileTableRow = _reflection.GeneratedProtocolMessageType('AieProfileTableRow', (_message.Message,), {
  'DESCRIPTOR' : _AIEPROFILETABLEROW,
  '__module__' : 'profiledata_pb2'
  # @@protoc_insertion_point(class_scope:xilinx.rigel.profile.v1.AieProfileTableRow)
  })
_sym_db.RegisterMessage(AieProfileTableRow)

AieLineGraph = _reflection.GeneratedProtocolMessageType('AieLineGraph', (_message.Message,), {
  'DESCRIPTOR' : _AIELINEGRAPH,
  '__module__' : 'profiledata_pb2'
  # @@protoc_insertion_point(class_scope:xilinx.rigel.profile.v1.AieLineGraph)
  })
_sym_db.RegisterMessage(AieLineGraph)


DESCRIPTOR._options = None
_PROFILESUMMODEL_SECTIONMAPENTRY._options = None
# @@protoc_insertion_point(module_scope)
