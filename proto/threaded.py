'''
The Proto! Python Async RPC based on ProtocolBuffers and TCP sockets.
Licensed under LPGLv2+.

Created on Oct 27, 2009
@author: Stanislav Yudin
'''
import threadpool
import logging

log = logging.getLogger(__name__)

class ProtoThreadServer(ProtoServer):
	pool = threadpool.ThreadPool(10)
	def handle_socket(self, socket):
		'''
		This method implemented in ProtoServer
		It is single thread handler for reading
		and processing data. Now we are going to
		call it inside thread

		args_list contains the parameters for each 
		invocation of callable. Each item in args_list 
		should be either a 2-item tuple of the list of 
		positional arguments and a dictionary of keyword 
		arguments or a single, non-tuple argument.
		'''
		args_list = [ ( [self, socket], None) ]
		r = threadpool.makeRequests(ProtoServer.handle_socket, args_list)[0]
		log.debug('starting child thread %s' % r)
		self.pool.putRequest(r)
		
