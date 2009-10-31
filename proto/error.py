'''
The Proto! Python Async RPC based on ProtocolBuffers and TCP sockets.
Licensed under LPGLv2+.

Created on  Oct 28, 2009
@author: Stanislav Yudin
'''
class ProtoDisconnected(Exception):
	pass

class ProtoError(Exception):
	pass
