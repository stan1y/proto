'''
The Proto! Python Async RPC based on Protobufers and TCP sokets.
Licenced under LPGLv2+.
Created on  Oct 24, 2009
@author: Stanislav Yudin
'''
import sys, logging
from proto import run_server, set_pb2_module
from k7talk_pb2 import *
import k7talk_pb2 as pb2
import k7impl as impl

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

if __name__ == '__main__':
	port = 9999
	if len(sys.argv) == 2:
		port = int(sys.argv[1])
	#running server with specific generated files and
	#module containing service implementation(s)
	run_server(port, pb2, impl)