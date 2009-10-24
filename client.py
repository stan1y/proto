'''
The Proto! Python Async RPC based on Protobufers and TCP sokets.
Licenced under LPGLv2+.
Created on  Oct 23, 2009

@author: Stanislav Yudin
'''
#proto library
from proto import ProtoChannel, ProtoController, ProtoError, set_module
#user
import k7talk_pb2 as k7mod
from k7talk_pb2 import *
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

def async_callback(answer):
	assert not answer == None

if __name__ == '__main__':
	log.info('client starting')
	server = K7TalkServer_Stub(ProtoChannel('localhost', 9999))
	set_module(k7mod)
	controller = ProtoController()
	login_ = K7_Login()
	login_.login = 'asd'
	login_.password = 'zxc'
	try:
		user_info  = server.login(controller, login_, async_callback)
		log.info('answer' + str(user_info))
		user_info  = server.login(controller, login_, async_callback)
		log.info('answer' + str(user_info))
		log.info('client done')
	except ProtoError, pe:
		log.error(str(pe))