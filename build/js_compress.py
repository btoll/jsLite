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
        --dest_dir      The location where the minified file will be moved, defaults to cwd.
        --src_dir       The location of the JSLITE source files, must be specified.
        --jar, -j       The location of the jar file, defaults to value of YUICOMPRESSOR environment variable.
        --version, -v   The version of the minified script, must be specified.
    '''
    print(textwrap.dedent(str))

def main(argv):
    jar = None
    dest_dir = '.'
    src_dir = ''
    version = ''

    try:
        opts, args = getopt.getopt(argv, 'hj:v:', ['help', 'version=', 'jar=', 'src_dir=', 'dest_dir='])
    except getopt.GetoptError:
        print('Error: Unrecognized flag.')
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif opt == '--dest_dir':
            dest_dir = arg
        elif opt == '--src_dir':
            src_dir = arg
        elif opt in ('-v', '--version'):
            version = arg
        elif opt in ('-j', '--jar'):
            jar = arg

    compress(version, src_dir, dest_dir, jar)

def compress(version, src_dir, dest_dir='.', jar=None):
    if not version:
        print('Error: You must provide a version.')
        sys.exit(2)

    if not src_dir:
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

    # The order is very important due to some dependencies between scripts, so specify the dependency order here.
    dependencies = [
        'JSLITE.prototype.js',
        'JSLITE.js',
        'JSLITE.Element.js',
        'JSLITE.Composite.js',
        'JSLITE.Observer.js'
    ]

    minified_script = 'JSLITE_' + version + '.min.js'
    copyright = '''\
        /*
         * jsLite {version!s}
         *
         * Copyright (c) 2009 - 2015 Benjamin Toll (benjamintoll.com)
         * Dual licensed under the MIT (MIT-LICENSE.txt)
         * and GPL (GPL-LICENSE.txt) licenses.
         *
         */
    '''.format(**locals())

    port = '22'
    dest_remote = '~'
    username = getpass.getuser()

    try:
        print('Creating minified script...\n')

        # Write to a buffer.
        buff = [textwrap.dedent(copyright)]

        genny = (dependencies + [os.path.basename(filepath) for filepath in glob.glob(src_dir + 'JSLITE*.js') if os.path.basename(filepath) not in dependencies])

        if (len(genny) - len(dependencies) <= 0):
            print('OPERATION ABORTED: No JSLITE source files were found in the specified source directory. Check your path?')
            sys.exit(1)

        for script in genny:
            buff.append(subprocess.getoutput('java -jar ' + jar + ' ' + src_dir + script))
            print('Script ' + script + ' minified.')

        # This will overwrite pre-existing.
        os.makedirs(dest_dir, exist_ok=True)
        with open(dest_dir + '/' + minified_script, mode='w', encoding='utf-8') as fp:
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

            p = subprocess.Popen(['scp', '-P', port, dest_dir + '/' + minified_script, username + '@example.com:' + dest_remote])
            sts = os.waitpid(p.pid, 0)
            print('Minified script ' + minified_script + ' pushed to ' + dest_remote + ' on remote server.')
        else:
            print('Created minified script ' + minified_script + ' in ' + dest_dir)

    except (KeyboardInterrupt):
        # Control-c sent a SIGINT to the process, handle it.
        print('\nProcess aborted!')
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
        sys.exit(2)

    main(sys.argv[1:])

