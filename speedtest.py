'''
Created on Oct 25, 2009

@author: Stanly
'''

import sys, logging, os, datetime, time
from proto import run_server, set_pb2_module
from k7talk_pb2 import *
import k7talk_pb2 as pb2
import k7impl as impl

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_10_calls():
	run(10)
def test_100_calls():
	run(100)
def test_1000_calls():
	run(1000)

def do_call(number):
	results = {}
	server = K7TalkServer_Stub(ProtoChannel('localhost', 9999, pb2))
	controller = ProtoController()
	login_ = K7_Login()
	login_.login = 'asd'
	login_.password = 'zxc'
	for i in xrange(1, number):
		before = datetime.time.now()
		user_info  = server.login(controller, login_, async_callback)
		after = datetime.time.now()
		results[i] = after - before
	log.info('calculating...')
	total = long(0)
	for i in xrange(1, number):
		total += results[i]
	return total / len(results)

def run(number):
	log.info('Starting speed test')
	pid = os.fork()
	if pid:
		try:
			log.info('waiting 5 seconds to let server start...')
			time.sleep(5)
			log.info('testing %s calls' % number)
			log.info('result: %s' % do_call())
		except ProtoError, pe:
			print 'ProtoError:', str(pe)
			sys.exit(1)
		
	else:
		#child runs server
		port = 9999
		if len(sys.argv) == 2:
			port = int(sys.argv[1])
		run_server(port, pb2, impl)
		