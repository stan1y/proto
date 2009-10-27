'''
The Proto! Python Async RPC based on Protobufers and TCP sokets.
Licenced under LPGLv2+.
Created on Oct 27, 2009
Version 0.0.2

References:
http://github.com/AwesomeStanly/proto
http://code.google.com/apis/protocolbuffers/

See README.txt for usage

@author: Stanislav Yudin
'''
import threadpool
import logging

log = logging.getLogger(__name__)
pool = threadpool.ThreadPool(10)

def ProtoThreadServer(ProtoServer):
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
		pool.putRequest(r)
		