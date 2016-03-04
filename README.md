# BitBucket CLI

A command-line helper for BitBucket. This program is inspired Chris Wanstrath's
wonderful [github command-line program](https://github.com/defunkt/github-gem),
and aims to expose a similar interface for BitBucket users. 

## Installation

    pip install bitbucket-cli

## Usage

The BitBucket CLI can be involked with either `bitbucket` or the shortened `bb` command:

    bitbucket <command> [options]


or


    bb <command> [options]


Most `bitbucket` commands take some or all of the following options:

    -h, --help                        show this help message and exit
    -u USERNAME, --username=USERNAME  your bitbucket username
    -p PASSWORD, --password=PASSWORD  your bitbucket password
    -o, --public                      make this repo public
    -c, --private                     make this repo private
    -P PROTOCOL, --protocol=PROTOCOL  which network protocol to use (https|ssh)

For `help` with any command:

    bb <command> --help

## Available Commands & Examples
	
`clone` an existing BitBucket repository:

    ...  bb clone --username <your-user-name> --protocol ssh zhemao bitbucket-cli 

`pull` a BitBucket repository:

    ...  bb pull <owner-name> <repo-name>

`create` a new BitBucket repository:

    ...  bb create --username <your-user-name> --public --protocol ssh <new-repo-name>

Creating a new BitBucket repository from an existing local repository is easy with `create_from_local`:

    ...  bb create_from_local --username <your-user-name> --public --protocol ssh <repo-owner> <repo-name>

`update` a BitBucket repository. Currently the only option is to change whether a repository is
*public* or *private*. This example will make the repository private:

    ...  bb update --username <user-name> --private <repo-name>

`delete` one of your BitBucket repository:

    ...  bb delete --username <your-user-name> <repo-name>

`pull_request` open a bitbucket pull request for current repo from source branch to destination branch:

    ...  bb pull_request --username <your-user-name> source destination


For the `clone`, `pull`, and `create_from_local` commands, the *scm* (either *git* or *hg*) will be 
detected from bitbucket or your local filesystem. Explicitly declaring the
*scm* on the command line or from the user configuration will not override it.


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
