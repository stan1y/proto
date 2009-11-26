'''
The Proto! Python Async RPC based on ProtocolBuffers and TCP sockets.
Licensed under LPGLv2+.

Created on  Oct 24, 2009
@author: Stanislav Yudin
'''
import pickle
from error import ProtoError

def encode_request(service_name, method_name, request_obj, response_class):
	request = {}
	packet = {}
	packet['service'] = service_name
	packet['method'] = method_name
	packet['request_class'] = type(request_obj).__name__
	packet['request'] = request_obj.SerializeToString()
	packet['response_class'] = response_class.__name__
	request['request'] = packet
	r = pickle.dumps(request)
	return r

def encode_answer(service_name, method_name, response, response_class):
	answer = {}
	packet = {}
	packet['service'] = service_name
	packet['method'] = method_name
	packet['response'] = response.SerializeToString()
	packet['response_class'] = response_class.__name__
	answer['answer']= packet
	a = pickle.dumps(answer)
	return a

def decode_request(data, module):
	request = pickle.loads(data)
	if not isinstance(request, dict) or not is_request(data):
		raise ProtoError('Invalid request for decoding')
	packet = request['request']
	if not isinstance(packet, dict):
		raise ProtoError('Invalid packet for decoding request')
	
	service_name = packet['service']
	method_name = packet['method']
	request_class = getattr(module, str(packet['request_class']))
	response_class = getattr(module, str(packet['response_class']))
	request_inst = request_class()
	request_inst.ParseFromString(packet['request'])
	return service_name, method_name, request_inst, response_class

def decode_answer(data, module):
	answer = pickle.loads(data)
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
	response_class = getattr(module,str(packet['response_class']))
	response_inst = response_class()
	response_inst.ParseFromString(packet['response'])
	return service_name, method_name, response_inst, response_class

def is_answer(data):
	answer = pickle.loads(data)
	if 'error' or 'answer' in answer:
		return True
	else:
		return False
	
def is_request(data):
	request = pickle.loads(data)
	if 'request' in request:
		return True
	else:
		return False
