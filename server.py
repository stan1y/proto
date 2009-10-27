'''
The Proto! Python Async RPC based on ProtocolBuffers and TCP sockets.
Licensed under LPGLv2+.

Created on  Oct 24, 2009
@author: Stanislav Yudin
'''
import sys, logging
import sample_pb2, proto, proto.threaded

log = logging.getLogger(__name__)

class sample_impl(proto.ProtoServer, sample_pb2.sample_rpc):
	def __init__(self, addr):
		proto.ProtoServer.__init__(self, addr)
		log.debug('starting service %s' % type(self).__name__)
	
	def the_method(self, rpc_controller, request, done):
		log.debug('%s called with %s' % (__name__, request))
		return sample_pb2.sample_response(answer = 'answer!')

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

if __name__ == '__main__':
	port = 9999
	if len(sys.argv) == 2:
		port = int(sys.argv[1])
	#running server with specific generated files and
	#module containing service implementation(s)
	sample_impl.run_server(port, sample_pb2)