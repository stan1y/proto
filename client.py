'''
The Proto! Python Async RPC based on Protobufers and TCP sokets.
Licenced under LPGLv2+.
Created on  Oct 23, 2009

@author: Stanislav Yudin
'''
import logging
import proto
import sample_pb2

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

def async_callback(answer):
	pass

if __name__ == '__main__':
	print 'client starting'
	#specifying generated classes
	server = sample_pb2.sample_rpc_Stub(proto.ProtoChannel('localhost', 9999, sample_pb2))
	controller = proto.ProtoController()
	try:
		rst = sample_pb2.sample_request( message = 'hello server!')
		resp = server.the_method(controller, rst, async_callback)
		print 'server answer %s' % str(resp.answer)

		print 'client done'
	except proto.ProtoError, pe:
		print 'ProtoError:', str(pe)