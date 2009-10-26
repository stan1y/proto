'''
Created on Oct 25, 2009

@author: Stanly
'''

import sys, logging, os, datetime, time
import proto
import sample_pb2

logging.basicConfig(filename='speedtest.log', level=logging.DEBUG)
log = logging.getLogger(__name__)

def test_10_calls():
	run(10)
def test_100_calls():
	run(100)
def test_1000_calls():
	run(1000)

def do_call(number):
	results = {}
	server = sample_pb2.sample_rpc_Stub(proto.ProtoChannel('localhost', 9999, sample_pb2))
	controller = proto.ProtoController()
	for i in xrange(1, number):
		before = datetime.time.now()
		rst = sample_pb2.sample_request( message = 'hello server!')
		assert server.the_method(controller, rst, async_callback) != None
		results[i] = after - before
	log.info('calculating...')
	total = long(0)
	for i in xrange(1, number):
		total += results[i]
	assert total > 0
	return total / len(results)

def run(number):
	log.info('Starting speed test')
	pid = os.fork()
	error = None
	if pid:
		try:
			log.info('waiting 5 seconds to let server start...')
			time.sleep(5)
			log.info('testing %s calls' % number)
			log.info('result: %s' % do_call(number))
		finally:
			os.kill(pid)
	else:
		#child runs server
		port = 9999
		if len(sys.argv) == 2:
			port = int(sys.argv[1])
		sample_impl.run_server(port, sample_pb2)
		