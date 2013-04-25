from setuptools import setup

setup(
	name = 'bitbucket-cli',
	version = '0.3.0',
	author = 'Zhehao Mao',
	author_email = 'zhehao.mao@gmail.com',
	description = 'BitBucket command line interface',
	packages = ['bitbucket'],
	install_requires = [ 'requests' ],
	entry_points = {
		'console_scripts': [
			'bitbucket = bitbucket.cli:run',
			'bb = bitbucket.cli:run'
		]
	}
)
