# TODO: support compressors other than YUI Compressor?

import getopt
import getpass
import glob
import os
import subprocess
import sys
import textwrap

def usage():
    str = '''
        Usage:
        --dependencies  A list of scripts, FIFO when compressed, default to an empty list..
        --output        The name of the new minimized file, defaults to 'min.js'.
        --dest          The location where the minified file will be moved, defaults to cwd.
        --src           The location of the JavaScript source files, must be specified.
        --jar, -j       The location of the jar file, defaults to value of YUICOMPRESSOR environment variable.
        --version, -v   The version of the minified script, must be specified.
    '''
    print(textwrap.dedent(str))

def main(argv):
    jar = None
    dest = '.'
    src = ''
    output = 'min.js'
    version = ''
    dependencies = []

    try:
        opts, args = getopt.getopt(argv, 'hj:v:', ['help', 'version=', 'output=', 'jar=', 'src=', 'dest='])
    except getopt.GetoptError:
        print('Error: Unrecognized flag.')
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif opt == '--dependencies':
            dependencies = arg
        elif opt == '--output':
            output = arg
        elif opt == '--dest':
            dest = arg
        elif opt == '--src':
            src = arg
        elif opt in ('-v', '--version'):
            version = arg
        elif opt in ('-j', '--jar'):
            jar = arg

    compress(version, src, output, dest, dependencies, jar)

def compress(version, src, output='min.js', dest='.', dependencies=[], jar=None):
    if not version:
        print('Error: You must provide a version.')
        sys.exit(2)

    if not src:
        print('Error: You must provide the location of the source files.')
        sys.exit(2)

    if not jar:
        # Provide an alternate location to the jar to override the environment variable (if set).
        jar = os.getenv('YUICOMPRESSOR')
        if not jar:
            jar = input('Location of YUI Compressor jar (set a YUICOMPRESSOR environment variable to skip this step): ')
            if not jar:
                print('Error: You must provide the location of YUI Compressor jar.')
                sys.exit(2)

    port = '22'
    dest_remote = '~'
    username = getpass.getuser()
    buff = []

    try:
        print('Creating minified script...\n')

        genny = (dependencies + [os.path.basename(filepath) for filepath in glob.glob(src + '*.js') if os.path.basename(filepath) not in dependencies])

        if (len(genny) - len(dependencies) <= 0):
            print('OPERATION ABORTED: No JavaScript source files were found in the specified source directory. Check your path?')
            sys.exit(1)

        for script in genny:
            buff.append(subprocess.getoutput('java -jar ' + jar + ' ' + src + script))
            print('Script ' + script + ' minified.')

        # This will overwrite pre-existing.
        os.makedirs(dest, exist_ok=True)
        # Let's append in case a build prepending copyright information (or anything, really) before calling here.
        with open(dest + '/' + output, mode='a', encoding='utf-8') as fp:
            # Flush the buffer (only perform I/O once).
            fp.write(''.join(buff))

        resp = input('\nPush to server? [y|N]: ')
        if resp in ['Y', 'y']:
            resp = input('Username [' + username + ']:')
            if resp != '':
                username = resp
            resp = input('Port [' + port + ']:')
            if resp != '':
                port = resp
            resp = input('Remote destination [' + dest_remote + ']:')
            if resp != '':
                dest_remote = resp

            p = subprocess.Popen(['scp', '-P', port, dest + '/' + output, username + '@example.com:' + dest_remote])
            sts = os.waitpid(p.pid, 0)
            print('Minified script ' + output + ' pushed to ' + dest_remote + ' on remote server.')
        else:
            print('Created minified script ' + output + ' in ' + dest)

    except (KeyboardInterrupt):
        # Control-c sent a SIGINT to the process, handle it.
        print('\nProcess aborted!')
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
        sys.exit(2)

    main(sys.argv[1:])

