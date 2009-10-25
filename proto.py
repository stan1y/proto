'''
The Proto! Python Async RPC based on Protobufers and TCP sokets.
Licenced under LPGLv2+.
Created on  Oct 24, 2009
Version 0.0.2

References:
http://github.com/AwesomeStanly/proto
http://code.google.com/apis/protocolbuffers/

Before using this rpc you need to create a protocol file and
generate python stubs and classes. To do it use
./protoc -python_out=. myprotocolfile.proto
So your 'myprotocolfile' will become myprotocolfile_pb2.py module.
You should supply it to 'run_server' method of your
rpc server implemenration. See server.py for reference

1. To create a rpc server
 - subclass ProtoServer and generated server class		class my_rpc_server_impl(ProtoServer, K7TalkServer):	"
 															def __init__(self, addr):							"
  																ProtoServer.__init__(self, addr)				"
 - import your generated module like.					import myprotocolfile_pb2 as pb2						"
 - start server											my_rpc_server_impl.run_server(port = 9999, pb2 = pb2)	"


@author: Stanislav Yudin
'''
from google.protobuf.service import RpcChannel, RpcController
import sys
import logging
import time
import socket
import threading
import SocketServer
import simplejson

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
		
class ProtoDisconnected(Exception):
	pass

class ProtoError(Exception):
	pass

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
	
	@classmethod	
	def run_server(cls, port, pb2):
		cls.run_server_thread(port, pb2)[1].join()
	
	@classmethod
	def run_server_thread(cls, port, pb2):
		set_pb2_module(pb2)
		log.info('Starting server for %s: %s' % ('localhost', port))
		server = cls(('localhost', port))
	    # Start a thread with the server -- that thread will then start one
	    # more thread for each request
		server_thread = threading.Thread(target=server.serve_forever)
	    # Exit the server thread when the main thread terminates
		server_thread.setDaemon(True)
		server_thread.start()
		#log.info("Server loop running in thread:", server_thread.getName())
		return server, server_thread
			
	# ************** Packet encoding and decoding ******************* #
	
	def serve_forever(self):
		self.sock.listen(10)
		while(True):
			"""
			Accepting connections
			"""
			log.info('Accepting connections..')
			try:
				connection, address = self.sock.accept()
				log.debug('Connection from %s:%s' % address)
				
				while(True):
					"""
					Reading packets
					"""
					log.info('Reading data from %s' % connection)
					data = recv_data(connection)
					
					#call method
					service_name, method_name, request_inst, response_class = decode_request(data)
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
					
					if c.Failed() or not res:
						log.fatal('rpc api %s.%s failed: %s' % (service_name, method_name, c.error) )
						#answer with error
						send_error_answer(connection, c.error)
					else:
				
						#create answer
						answer = encode_answer(service_name, method_name, res, response_class)
						send_data(connection,answer)
						log.info('rpc call %s.%s finished' % (service_name, method_name))
					continue #reading	
						
			except ProtoDisconnected, pd:
				log.info('disconnected (%s) %s' % (type(pd), str(pd)) )
				log.info('closing clinet connection,,,')
				connection.close()
				continue #accepting
		
	def callback(self, object):
		log.info('callback: %s', object)
   
def encode_request(service_name, method_name, request_obj, response_class):
	request = {}
	packet = {}
	packet['service'] = service_name
	packet['method'] = method_name
	packet['request_class'] = type(request_obj).__name__
	packet['request'] = request_obj.SerializeToString()
	packet['response_class'] = response_class.__name__
	request['request'] = packet
	r = simplejson.dumps(request)
	return r

def encode_answer(service_name, method_name, response, response_class):
	answer = {}
	packet = {}
	packet['service'] = service_name
	packet['method'] = method_name
	packet['response'] = response.SerializeToString()
	packet['response_class'] = response_class.__name__
	answer['answer']= packet
	a = simplejson.dumps(answer)
	return a

def decode_request(data):
	request = simplejson.loads(data)
	if not isinstance(request, dict) or not is_request(data):
		raise ProtoError('Invalid request for decoding')
	packet = request['request']
	if not isinstance(packet, dict):
		raise ProtoError('Invalid packet for decoding request')
	
	service_name = packet['service']
	method_name = packet['method']
	request_class = getattr(get_pb2_module(),str(packet['request_class']))
	request_inst = request_class()
	request_inst.ParseFromString(packet['request'])
	response_class = getattr(get_pb2_module(), str(packet['response_class']))
	return service_name, method_name, request_inst, response_class

def decode_answer(data):
	answer = simplejson.loads(data)
	if not isinstance(answer, dict) or not is_answer(data):
		raise ProtoError('Invalid answer for decoding')
	
	#check for error
	if 'error' in answer:
		raise ProtoError(answer['error'])
	
	packet = answer['answer']
	if not isinstance(packet, dict):
		raise ProtoError('Invalid packet for decoding answer')
	
	service_name = packet['service']
	method_name = packet['method']
	response_class = getattr(get_pb2_module(),str(packet['response_class']))
	response_inst = response_class()
	response_inst.ParseFromString(packet['response'])
	return service_name, method_name, response_inst, response_class

def is_answer(data):
	answer = simplejson.loads(data)
	if 'error' or 'answer' in answer:
		return True
	else:
		return False
	
def is_request(data):
	request = simplejson.loads(data)
	if 'request' in request:
		return True
	else:
		return False
	
# ************** Send % Receive ******************* #

def recv_data(the_socket):
	log.debug('reading data...')
	data = the_socket.recv(8192)
	if not data:
		log.debug('socket disconnected!')
		raise ProtoDisconnected()
	log.debug('received %s bytes' % len(data))
	return data		

def send_data(sock,data):
	sent_bytes = sock.send(data)
	log.debug('sent %s bytes' % sent_bytes)
	
def send_error_answer(sock, error):
	p = simplejson.dumps({ 'error': error })
	log.debug('rpc sending error: %s' % p)
	send_data(sock, p)

def request_with_answer(sock, request):
	send_data(sock, request)
	data = recv_data(sock)
	if not data or len(data) < 0:
		raise ProtoError('No data received as response')
	if is_answer(data):
		#answer received, exiting while and return
		log.debug('Gochaa! (%s) : %s' % (len(data), data))
		return decode_answer(data)
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
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		log.info('opening channel to %s:%s' % (host, port))
		self.sock.connect((host, port))		
	
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
		
		request = encode_request(md.containing_service.name, md.name, request, response_class)
		service_name, method_name, response_inst, response_class = request_with_answer(self.sock, request)
		
		log.debug('answer method_name: %s' % method_name)
		log.debug('answer service_name: %s' % service_name)
		log.debug('answer response_inst: %s' % response_inst)
		log.debug('answer response_class: %s' % response_class)
		#callback
		if done:
			done(response_inst)
		
		log.debug('call finished')
		return response_inst