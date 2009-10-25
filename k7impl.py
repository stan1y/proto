'''
Created on Oct 24, 2009

@author: Stanly
'''
from proto import ProtoServer
from k7talk_pb2 import K7TalkServer, K7_Login, K7_UserInfo
import logging

log = logging.getLogger(__name__)

class K7TalkServerImplementation(ProtoServer, K7TalkServer):
	def __init__(self, addr):
		ProtoServer.__init__(self, addr)
		log.debug('starting service %s' % type(self).__name__)
	
	def login(self, rpc_controller, request, done):
		log.info('[IN] %s.login' % __name__)
		return K7_UserInfo( id = 1, 
						first_name = 'John', 
						last_name = 'Smith',
						login = K7_Login( login = 'johnsmith')
						)