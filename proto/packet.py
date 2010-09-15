'''
The Proto! Python Async RPC based on ProtocolBuffers and TCP sockets.
Licensed under LPGLv2+.

Created on	Oct 24, 2009
@author: Stanislav Yudin
'''
from pyasn1.type import univ, namedtype
from pyasn1.codec.der import encoder, decoder
from error import ProtoError
import logging

class ProtoPacketPayload(univ.OctetString):
	pass

class ProtoRequestAsn1(univ.Sequence):
	componentType = namedtype.NamedTypes(
		namedtype.NamedType('service', univ.OctetString()),
		namedtype.NamedType('method', univ.OctetString()),
		namedtype.NamedType('request_class', univ.OctetString()),
		namedtype.NamedType('request', ProtoPacketPayload()),
		namedtype.NamedType('response_class', univ.OctetString())
	)

class ProtoResponseAsn1(univ.Sequence):
	componentType = namedtype.NamedTypes(
		namedtype.NamedType('service', univ.OctetString()),
		namedtype.NamedType('method', univ.OctetString()),
		namedtype.NamedType('response', ProtoPacketPayload()),
		namedtype.NamedType('response_class', univ.OctetString()),
		namedtype.NamedType('error', univ.OctetString())
	)

def encode_request(service_name, method_name, request_obj, response_class):
	pkt = ProtoRequestAsn1()
	pkt.setComponentByPosition(0, service_name)
	pkt.setComponentByPosition(1, method_name)
	pkt.setComponentByPosition(2, type(request_obj).__name__)
	pkt.setComponentByPosition(3, request_obj.SerializeToString())
	pkt.setComponentByPosition(4, response_class.__name__)
	return encoder.encode(pkt)

def encode_answer(service_name, method_name, response, response_class):
	pkt = ProtoResponseAsn1()
	pkt.setComponentByPosition(0, service_name)
	pkt.setComponentByPosition(1, method_name)
	pkt.setComponentByPosition(2, response.SerializeToString())
	pkt.setComponentByPosition(3, response_class.__name__)
	pkt.setComponentByPosition(4, '')
	return encoder.encode(pkt)
	
def encode_error(service_name, method_name, error):
	pkt = ProtoResponseAsn1()
	pkt.setComponentByPosition(0, service_name)
	pkt.setComponentByPosition(1, method_name)
	pkt.setComponentByPosition(2, '')
	pkt.setComponentByPosition(3, '')
	pkt.setComponentByPosition(4, error)
	return encoder.encode(pkt)

def decode_request(data, module):
	pkt = decoder.decode(data, asn1Spec = ProtoRequestAsn1())[0]
	if not pkt:
		raise ProtoError('Invalid packet for decoding request')
	
	service_name = str(pkt.getComponentByPosition(0))
	method_name = str(pkt.getComponentByPosition(1))
	
	request_class = getattr(module, str(pkt.getComponentByPosition(2)))
	request_inst = request_class()
	request_inst.ParseFromString( str(pkt.getComponentByPosition(3)) )
	
	response_class = getattr(module, str(pkt.getComponentByPosition(4)))
	return service_name, method_name, request_inst, response_class

def decode_answer(data, response_type):
	pkt = decoder.decode(data, asn1Spec = ProtoResponseAsn1())[0]
	if not pkt:
		raise ProtoError('Invalid packet for decoding response')
	
	#check for error
	error = str(pkt.getComponentByPosition(4))
	if error and len(error) > 0:
		raise ProtoError(error)
	
	response_type_name = str(pkt.getComponentByPosition(3))
	if response_type.__name__ != response_type_name:
		raise ProtoError('Response type %s received when %d was expected' % (response_type_name, response_type.__name__))
	
	#get data
	service_name = str(pkt.getComponentByPosition(0))
	method_name = str(pkt.getComponentByPosition(1))
	response_inst = response_type()
	response_inst.ParseFromString( str(pkt.getComponentByPosition(2)) )
	return service_name, method_name, response_inst
