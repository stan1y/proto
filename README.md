## The Proto! Python Async RPC based on ProtocolBuffers and TCP sockets.##

The Proto is a simple RPC implementation on top of ProtocolBuffers rpc stubs. It uses TCP sockets to
talk and ASN.1 to encode packets with your ProtocolBuffer message & some meta data for rpc.

Based on:
- http://github.com/AwesomeStanly/proto
- http://code.google.com/apis/protocolbuffers/

Current version: **0.4.0**

### Server Sample ###

Before using this RPC module you need to create a protocol file and generate python stubs and classes.
    ./protoc -python_out=. myprotocolfile.proto
So your 'myprotocolfile' will become myprotocolfile_pb2.py module. You should supply it to 'run_server' method of your rpc server implementation. See server.py for reference. You need to:

- Subclass ProtoServer and generated server class (MyRPCServer is example)

      class MyRPCServerImpl(ProtoServer, MyRPCServer):
        def __init__(self, addr):
          ProtoServer.__init__(self, addr)

- import your generated module.
      import myprotocolfile_pb2

- start server
      MyRPCServerImpl.run_server(port = 9999, pb2 = myprotocolfile_pb2)

### Client Sample ###

See client.py for working example

    from myprotocolfile_pb2 import MyRequestClass
    rpc_server = MyRPCServer_Stub(ProtoChannel('localhost', 9999, pb2))
    controller = ProtoController()
    try:
      r = MyRequestClass()
      response  = rpc_server.my_rpc_method(controller, r, None)
      if response: print 'response %s' % str(response)
    except ProtoError, pe:
      print 'ProtoError:', str(pe)
