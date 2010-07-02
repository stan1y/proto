try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
		name='proto',
		version='0.3.2',
		description="The \"Proto!\" Python Async RPC based on ProtocolBuffers and TCP sockets.",
		author="Stanislav Yudin",
		author_email="decvar@gmail.com",
		url="http://github.com/AwesomeStanly/proto",
		classifiers=["Development Status :: Beta", "Framework :: ProtocolBuffers"],
		include_package_data=True,
		install_requires=[ "protobuf>=2.2.0a"],
		packages=['proto'],
		setup_requires=[],
		zip_safe=True
	)
