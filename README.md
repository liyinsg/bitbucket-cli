# BitBucket CLI

A command-line helper for BitBucket. This program is inspired Chris Wanstrath's
wonderful [github command-line program](https://github.com/defunkt/github-gem),
and aims to expose a similar interface for BitBucket users. 

## Installation

    pip install bitbucket-cli

## Usage

    bitbucket command [options]

## Available Commands
	
    clone username reponame

    pull username reponame

    create reponame

    create-from-local

    update username reponame

    delete username reponame

## Options

    -h, --help                        show this help message and exit
    -u USERNAME, --username=USERNAME  your bitbucket username
    -p PASSWORD, --password=PASSWORD  your bitbucket password
    -o, --public                      make this repo public
    -c, --private                     make this repo private
    -P PROTOCOL, --protocol=PROTOCOL  which network protocol to use (https|ssh)

## Configuration

You can create a configuration file in ~/.bitbucket that follows the following
format

    [auth]
    username = <Your Username>
    password = <Your Password>
    
    [options]
    scm = <'git' or 'hg'>
    protocol = <'https' or 'ssh'>

It will provide default options which can be overridden on the command line.

For the `clone`, `pull`, and `create-from-local` commands, the scm will be 
detected from bitbucket or your local filesystem. Explicitly declaring the
scm on the command line or from the user configuration will not override it.
