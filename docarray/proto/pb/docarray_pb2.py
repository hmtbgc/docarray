# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: docarray.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0e\x64ocarray.proto\x12\x08\x64ocarray\x1a\x1cgoogle/protobuf/struct.proto\"A\n\x11\x44\x65nseNdArrayProto\x12\x0e\n\x06\x62uffer\x18\x01 \x01(\x0c\x12\r\n\x05shape\x18\x02 \x03(\r\x12\r\n\x05\x64type\x18\x03 \x01(\t\"g\n\x0cNdArrayProto\x12*\n\x05\x64\x65nse\x18\x01 \x01(\x0b\x32\x1b.docarray.DenseNdArrayProto\x12+\n\nparameters\x18\x02 \x01(\x0b\x32\x17.google.protobuf.Struct\"Z\n\x0cKeyValuePair\x12#\n\x03key\x18\x01 \x01(\x0b\x32\x16.google.protobuf.Value\x12%\n\x05value\x18\x02 \x01(\x0b\x32\x16.google.protobuf.Value\";\n\x10GenericDictValue\x12\'\n\x07\x65ntries\x18\x01 \x03(\x0b\x32\x16.docarray.KeyValuePair\"\xcb\x03\n\tNodeProto\x12\x0e\n\x04text\x18\x01 \x01(\tH\x00\x12\x11\n\x07integer\x18\x02 \x01(\x05H\x00\x12\x0f\n\x05\x66loat\x18\x03 \x01(\x01H\x00\x12\x11\n\x07\x62oolean\x18\x04 \x01(\x08H\x00\x12\x0e\n\x04\x62lob\x18\x05 \x01(\x0cH\x00\x12)\n\x07ndarray\x18\x06 \x01(\x0b\x32\x16.docarray.NdArrayProtoH\x00\x12+\n\x08\x64ocument\x18\x07 \x01(\x0b\x32\x17.docarray.DocumentProtoH\x00\x12\x36\n\x0e\x64ocument_array\x18\x08 \x01(\x0b\x32\x1c.docarray.DocumentArrayProtoH\x00\x12*\n\x04list\x18\t \x01(\x0b\x32\x1a.google.protobuf.ListValueH\x00\x12)\n\x03set\x18\n \x01(\x0b\x32\x1a.google.protobuf.ListValueH\x00\x12+\n\x05tuple\x18\x0b \x01(\x0b\x32\x1a.google.protobuf.ListValueH\x00\x12\'\n\x04\x64ict\x18\x0c \x01(\x0b\x32\x17.google.protobuf.StructH\x00\x12\x0e\n\x04type\x18\r \x01(\tH\x01\x42\t\n\x07\x63ontentB\x0f\n\rdocarray_type\"\x82\x01\n\rDocumentProto\x12/\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32!.docarray.DocumentProto.DataEntry\x1a@\n\tDataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\"\n\x05value\x18\x02 \x01(\x0b\x32\x13.docarray.NodeProto:\x02\x38\x01\";\n\x12\x44ocumentArrayProto\x12%\n\x04\x64ocs\x18\x01 \x03(\x0b\x32\x17.docarray.DocumentProto\"\x88\x03\n\x19\x44ocumentArrayStackedProto\x12+\n\x05list_\x18\x01 \x01(\x0b\x32\x1c.docarray.DocumentArrayProto\x12H\n\x0b\x64oc_columns\x18\x02 \x03(\x0b\x32\x33.docarray.DocumentArrayStackedProto.DocColumnsEntry\x12N\n\x0etensor_columns\x18\x03 \x03(\x0b\x32\x36.docarray.DocumentArrayStackedProto.TensorColumnsEntry\x1aV\n\x0f\x44ocColumnsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x32\n\x05value\x18\x02 \x01(\x0b\x32#.docarray.DocumentArrayStackedProto:\x02\x38\x01\x1aL\n\x12TensorColumnsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12%\n\x05value\x18\x02 \x01(\x0b\x32\x16.docarray.NdArrayProto:\x02\x38\x01\x62\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'docarray_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    _DOCUMENTPROTO_DATAENTRY._options = None
    _DOCUMENTPROTO_DATAENTRY._serialized_options = b'8\001'
    _DOCUMENTARRAYSTACKEDPROTO_DOCCOLUMNSENTRY._options = None
    _DOCUMENTARRAYSTACKEDPROTO_DOCCOLUMNSENTRY._serialized_options = b'8\001'
    _DOCUMENTARRAYSTACKEDPROTO_TENSORCOLUMNSENTRY._options = None
    _DOCUMENTARRAYSTACKEDPROTO_TENSORCOLUMNSENTRY._serialized_options = b'8\001'
    _DENSENDARRAYPROTO._serialized_start = 58
    _DENSENDARRAYPROTO._serialized_end = 123
    _NDARRAYPROTO._serialized_start = 125
    _NDARRAYPROTO._serialized_end = 228
    _KEYVALUEPAIR._serialized_start = 230
    _KEYVALUEPAIR._serialized_end = 320
    _GENERICDICTVALUE._serialized_start = 322
    _GENERICDICTVALUE._serialized_end = 381
    _NODEPROTO._serialized_start = 384
    _NODEPROTO._serialized_end = 843
    _DOCUMENTPROTO._serialized_start = 846
    _DOCUMENTPROTO._serialized_end = 976
    _DOCUMENTPROTO_DATAENTRY._serialized_start = 912
    _DOCUMENTPROTO_DATAENTRY._serialized_end = 976
    _DOCUMENTARRAYPROTO._serialized_start = 978
    _DOCUMENTARRAYPROTO._serialized_end = 1037
    _DOCUMENTARRAYSTACKEDPROTO._serialized_start = 1040
    _DOCUMENTARRAYSTACKEDPROTO._serialized_end = 1432
    _DOCUMENTARRAYSTACKEDPROTO_DOCCOLUMNSENTRY._serialized_start = 1268
    _DOCUMENTARRAYSTACKEDPROTO_DOCCOLUMNSENTRY._serialized_end = 1354
    _DOCUMENTARRAYSTACKEDPROTO_TENSORCOLUMNSENTRY._serialized_start = 1356
    _DOCUMENTARRAYSTACKEDPROTO_TENSORCOLUMNSENTRY._serialized_end = 1432
# @@protoc_insertion_point(module_scope)