The Proto! Python Async RPC based on ProtocolBuffers and TCP sockets.
Licenced under LPGLv2+.
Created on  Oct 24, 2009
Version 0.3.1

References:
http://github.com/AwesomeStanly/proto
http://code.google.com/apis/protocolbuffers/

Before using this RPC module you need to create a protocol file and
generate python stubs and classes. To do it use
./protoc -python_out=. myprotocolfile.proto
So your 'myprotocolfile' will become myprotocolfile_pb2.py module.
You should supply it to 'run_server' method of your
rpc server implementation. See server.py for reference.

1. To create a rpc server. See server.py for working example

 A. subclass ProtoServer and generated server class (MyRPCServer is example)
<pre>
class MyRPCServerImpl(ProtoServer, MyRPCServer):
	def __init__(self, addr):
		ProtoServer.__init__(self, addr)
</pre>
 B. import your generated module.
 <pre>import myprotocolfile_pb2</pre>
 C. start server
 <pre>MyRPCServerImpl.run_server(port = 9999, pb2 = myprotocolfile_pb2)</pre>

2. To create a rpc client. See client.py for working example
<pre>
	from myprotocolfile_pb2 import MyRequestClass
	rpc_server = MyRPCServer_Stub(ProtoChannel('localhost', 9999, pb2))
	controller = ProtoController()
	try:
		r = MyRequestClass()
		response  = rpc_server.my_rpc_method(controller, r, None)
		if response: print 'response %s' % str(response)
	except ProtoError, pe:
		print 'ProtoError:', str(pe)
</pre>
