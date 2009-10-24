'''
The Proto! Python Async RPC based on Protobufers and TCP sokets.
Licenced under LPGLv2+.
Created on  Oct 23, 2009

@author: Stanislav Yudin
'''
#proto library imports
from proto import ProtoChannel, ProtoController, ProtoError, set_pb2_module
#pb2 generated module
import k7talk_pb2 as pb2
#user imports
from k7talk_pb2 import K7_Login, K7TalkServer_Stub
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

def async_callback(answer):
	assert not answer == None

if __name__ == '__main__':
	print 'client starting'
	#specifying generated classes
	server = K7TalkServer_Stub(ProtoChannel('localhost', 9999, pb2))
	controller = ProtoController()
	try:
		login_ = K7_Login()
		login_.login = 'asd'
		login_.password = 'zxc'
		user_info  = server.login(controller, login_, async_callback)
		print 'login answer %s' % str(user_info)
		
		
		s_ = K7_SignIn()
		s_.app_name = 'my-app'
		s_.user = user_info
		app_info  = server.signin_app(controller, login_, async_callback)
		print 'signin_app %s' % app_info
		
		print 'client done'
	except ProtoError, pe:
		print str(pe)