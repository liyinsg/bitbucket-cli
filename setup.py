from setuptools import setup

setup(
	name = 'bitbucket-cli',
	version = '0.1',
	author = 'Zhehao Mao',
	author_email = 'zhehao.mao@gmail.com',
	packages = ['bitbucket'],
	install_requires = [ 'requests' ],
	entry_points = {
		'console_scripts': [
			'bitbucket = bitbucket.cli:run',
			'bb = bitbucket.cli:run'
		]
	}
)
