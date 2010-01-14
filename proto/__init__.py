'''
The Proto! Python Async RPC based on ProtocolBuffers and TCP sockets.
Licensed under LPGLv2+.
Created on  Oct 24, 2009

@version: 0.3.1

References:
http://github.com/AwesomeStanly/proto
http://code.google.com/apis/protocolbuffers/

See README.txt for usage

@author: Stanislav Yudin
'''
from google.protobuf.service import RpcChannel, RpcController
import sys
import logging
import time
import socket
import threading
import simplejson
import packet
from error import *

log = logging.getLogger(__name__)
SIZE = 8192

__pb2_module = None

def get_pb2_module():
	global __pb2_module
	return __pb2_module

def set_pb2_module(module):
	global __pb2_module
	if not __pb2_module:
		__pb2_module = module

# ************** RPC Controller ******************* #

class ProtoController(RpcController):
	error = None

	def Reset(self):
		"""
		Resets the RpcController to its initial state. 	source code
		"""
		self.error = None
  	
	def Failed(self):
		"""
		Returns true if the call failed. 	source code
		"""
		return self.error
  	
	def ErrorText(self):
		"""
		If Failed is true, returns a human-readable description of the error. 	source code
		"""
	 	return self.error
  	
	def StartCancel(self):
		"""
		Initiate cancellation. 	source code
		"""
		pass

	def SetFailed(self, reason):
		"""
		Sets a failure reason. 	source code
	  	"""
	  	self.error = reason
  	
  	def IsCanceled(self):
	  	"""
	  	Checks if the client cancelled the RPC. 	source code
	  	"""
	  	return false
	  	
  	def NotifyOnCancel(self, callback):
  		log.error('notify: %s' % callback)
  		pass

# ************** Server ******************* #

class ProtoServer(object):
	def __init__(self, addr):
		self.addr = addr
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind(addr)
		log.debug('%s listening on %s' % (type(self).__name__, addr))
	
	@classmethod	
	def run_server(cls, port):
		cls.run_server_thread(port)[1].join()
	
	@classmethod
	def run_server_thread(cls, port):
		log.info('Starting %s on %s: %s' % ( cls.__name__, 'localhost', port))
		server = cls(('localhost', port))
	    # Start a thread with the server -- that thread will then start one
	    # more thread for each request
		server_thread = threading.Thread(target=server.serve_forever)
		server_thread.start()
		#log.info("Server loop running in thread:", server_thread.getName())
		return server, server_thread
	
	def serve_forever(self):
		'''
			Main server entry point
		'''
		self.sock.listen(10)
		while(True):
			"""
			Accepting connections
			"""
			log.info('Accepting connections..')
			try:
				try:
					connection, address = self.sock.accept()
					socket = ProtoSocket(connection)
					self.handle_socket(socket)
					log.debug('Connection from %s:%s' % address)
				except ProtoDisconnected, pd:
					log.info('Disconnected (%s) %s' % (type(pd), str(pd)) )
					continue #accepting
			finally:
				log.info('Closing clinet connection...')
				connection.close()

	def callback(self, object):
		log.info('callback: %s', object)
			
	def handle_socket(self, socket):
		while(True):
			"""
			Reading packets
			"""
			log.info('Reading data from %s' % socket)
			data = socket.recv_data()
			#call method
			service_name, method_name, request_inst, response_class = packet.decode_request(data, get_pb2_module())
			log.info('rpc api %s.%s started' % (type(self).__name__, method_name))
			log.debug('rpc service object: %s (%s)' % (service_name, getattr(get_pb2_module(), service_name)))
			if not isinstance(self, getattr(get_pb2_module(), service_name) ):
				raise ProtoError('method %s expects service class %s, but found %s' %
								( method_name, service_name, type(self).__name__ )
								)
					
			done = None
			c = ProtoController()
			#creating implementation of requested server
			method = self.GetDescriptor().FindMethodByName(method_name)
			if not method:
				log.fatal('Failed to find method %s' % method_name)
				raise ProtoError('Failed to find method %s' % method_name)
			
			log.debug('rpc method : %s %s.%s() (%s)' % ( response_class.__name__, 
														service_name,
														method.name,
														method )
														)
				
			res = self.CallMethod(method, c, request_inst, self.callback)
			
			if res is None:
				log.fatal('rpc api %s.%s returned None'  % (service_name, method_name))
				socket.send_error_answer('No RPC response')
			elif c.Failed():
				log.fatal('rpc api %s.%s failed: %s' % (service_name, method_name, c.error) )
				#answer with error
				socket.send_error_answer(c.error)
			else:
				#create answer
				answer = packet.encode_answer(service_name, method_name, res, response_class)
				socket.send_data(answer)
				log.info('rpc call %s.%s finished' % (service_name, method_name))
			continue #reading	
	
class ProtoSocket(object):
	def __init__(self, socket):
		self.__socket = socket
		
	def close(self):
		self.__socket.close()
		log.info('closing socket...')
	
	def recv_data(self):
		log.debug('reading data...')
		data = self.__socket.recv(8192)
		if not data:
			log.debug('socket disconnected!')
			raise ProtoDisconnected()
		log.debug('received %s bytes' % len(data))
		return data		
	
	def send_data(self, data):
		sent_bytes = self.__socket.send(data)
		log.debug('sent %s bytes' % sent_bytes)
		
	def send_error_answer(self, error):
		p = simplejson.dumps({ 'error': error })
		log.debug('rpc sending error: %s' % p)
		self.send_data(p)
	
	def request_with_answer(self, request):
		self.send_data(request)
		data = self.recv_data()
		if not data or len(data) < 0:
			raise ProtoError('No data received as response')
		if packet.is_answer(data):
			#answer received, exiting while and return
			log.debug('Gochaa! (%s) : %s' % (len(data), data))
			return packet.decode_answer(data, get_pb2_module())
		else:
			log.debug('received some strange data while waiting for answer...')
		

# ************** Client ******************* #

class ProtoChannel(RpcChannel):
	"""
		Client access 
	"""
	def __init__(self, host, port, pb2):
		set_pb2_module(pb2)
		self.host = host
		self.port = port
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host, port))
		log.info('opening channel to %s:%s' % (host, port))
		self.sock = ProtoSocket(s)
	
	def CallMethod(self, md, rpc_controller, request, response_class, done):
		"""
			Calls the method identified by the descriptor.

			Call the given method of the remote service. 
			The signature of this procedure looks the same as Service.CallMethod(), 
			but the requirements are less strict in one important way: the request 
			object doesn't have to be of any specific class as long as its 
			descriptor is method.input_type.
		"""
		log.debug('API proxy call: %s' % md.name)
		log.debug('Service name: %s' % md.containing_service.name)
		log.debug('Method object: %s - %s' % ( md.name, md ))
		log.debug('Request object: %s' % (type(request)))
		log.debug('Response class: %s' % response_class)
		
		request = packet.encode_request(md.containing_service.name, md.name, request, response_class)
		service_name, method_name, response_inst, response_class = self.sock.request_with_answer(request)
		
		log.debug('answer method_name: %s' % method_name)
		log.debug('answer service_name: %s' % service_name)
		log.debug('answer response_inst: %s' % response_inst)
		log.debug('answer response_class: %s' % response_class)
		#callback
		if done:
			done(response_inst)
		
		log.debug('call finished')
		return response_inst
