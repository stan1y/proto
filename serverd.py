'''
Created on Oct 26, 2009

@author: Stanly

Multi threaded RPC daemon
'''
import os, sys, logging
import daemon
import server
import proto
import sample_pb2

log = logging.getLogger(__name__)

class sample_daemon(daemon.Daemon, server.sample_impl):
	def __init__(self, addr):
		daemon.Daemon.__init__(self, pidfile = '.serverd_pidfile')
		server.sample_impl.__init__(self, addr)
		
	def run(self):
		self.serve_forever()
		
if __name__ == '__main__':
	proto.set_pb2_module(sample_pb2)
	port = 9999
	if len(sys.argv) == 3:
		port = int(sys.argv[2])
		
	daemon = sample_daemon(('localhost', port))
	if len(sys.argv) == 2:
		action = str(sys.argv[1])
		if action == 'start':
			daemon.start()
		elif action == 'stop':
			daemon.stop()
		elif action == 'restart':
			daemon.restart()
		else:
			log.fatal('unknown command %s' % action)
		sys.exit(0)
	else:
		print 'Usage: %s start|stop|restart [port]' % sys.argv[0]
