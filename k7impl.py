'''
Created on Oct 24, 2009

@author: Stanly
'''
from k7talk_pb2 import K7TalkServer, K7_Login, K7_UserInfo
import logging

log = logging.getLogger(__name__)

class K7TalkServerImpl(K7TalkServer):
	def login(self, rpc_controller, request, done):
		log.info('login implementation called')
		return K7_UserInfo( id = 1, 
						first_name = 'John', 
						last_name = 'Smith',
						login = K7_Login( login = 'johnsmith')
						)