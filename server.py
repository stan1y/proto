'''
The Proto! Python Async RPC based on Protobufers and TCP sokets.
Licenced under LPGLv2+.
Created on  Oct 24, 2009
@author: Stanislav Yudin
'''
import sys, logging
from proto import run_server, set_module
import k7talk_pb2 as k7mod
from k7talk_pb2 import *

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

if __name__ == '__main__':
	port = 9999
	if len(sys.argv) == 2:
		port = int(sys.argv[1])
	set_module(k7mod)
	run_server(port)