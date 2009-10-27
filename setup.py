from distutils.core import setup

setup(
		name='proto',
		version='0.3.1',
		packages=['proto']
		description = "The Proto! Python Async RPC based on ProtocolBuffers and TCP sockets.",
		author = "Stanislav Yudin"
		author_email = "decvar@gmail.com",
		classifiers = ["Development Status :: Beta", "Framework :: ProtocolBuffers"],
		include_package_data = True,
	)