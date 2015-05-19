import getopt
import getpass
import glob
import os
import subprocess
import sys
import textwrap
import time

def usage():
    str = '''
        Usage:
        --dest_dir      The location where the minified file will be moved, defaults to cwd.
        --jar           The location of the jar file, defaults to '/usr/local/src/yuicompressor-2.4.8.jar'.
        --src_dir       The location of the JSLITE source files, defaults to '/usr/local/www/public/dev/jslite/lib/js/'.
        --version, -v   The version of the minified script, must be specified.
    '''
    print(textwrap.dedent(str))

def main(argv):
    JAR_FILE = '/path/to/yuicompressor-2.4.8.jar'
    DEST_DIR = '.'
    SRC_DIR = ''
    VERSION = ''

    try:
        opts, args = getopt.getopt(argv, 'hv:', ['help', 'version=', 'jar=', 'src_dir=', 'dest_dir='])
    except getopt.GetoptError:
        print('Error: Unrecognized flag.')
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif opt in ('-v', '--version'):
            VERSION = arg
        elif opt == '--jar':
            JAR_FILE = arg
        elif opt == '--src_dir':
            SRC_DIR = arg
        elif opt == '--dest_dir':
            DEST_DIR = arg

    if not (SRC_DIR):
        print('Error: You must provide the location of the source files.')
        sys.exit(2)

    if not (VERSION):
        print('Error: You must provide a version.')
        sys.exit(2)

    # The order is very important due to some dependencies between scripts, so specify the dependency order here.
    FIRST_IN_FILES = [
        'JSLITE.prototype.js',
        'JSLITE.js',
        'JSLITE.Element.js',
        'JSLITE.Composite.js',
        'JSLITE.Observer.js'
    ]

    MINIFIED_SCRIPT = 'JSLITE_' + VERSION + '.min.js'
    COPYRIGHT = '''\
        /*
         * jsLite {VERSION!s}
         *
         * Copyright (c) 2009 - 2015 Benjamin Toll (benjamintoll.com)
         * Dual licensed under the MIT (MIT-LICENSE.txt)
         * and GPL (GPL-LICENSE.txt) licenses.
         *
         */
    '''.format(**locals())

    PORT = '22'
    DEST_REMOTE = '~'
    USERNAME = getpass.getuser()

    try:
        print('Creating minified script...\n')

        # Write to a buffer.
        content = [textwrap.dedent(COPYRIGHT)]

        genny = (FIRST_IN_FILES + [os.path.basename(filepath) for filepath in glob.glob(SRC_DIR + 'JSLITE*.js') if os.path.basename(filepath) not in FIRST_IN_FILES])

        if len(genny) == 2:
            print('OPERATION ABORTED: No JSLITE source files were found in the specified source directory. Check your path?')
            sys.exit(1)

        for script in genny:
            begin = int(time.time())
            content.append(subprocess.getoutput('java -jar ' + JAR_FILE + ' ' + SRC_DIR + script))
            end = int(time.time())
            print('Script ' + script + ' minified in ' + str(end - begin) + 's')

        # This will overwrite pre-existing.
        with open(DEST_DIR + '/' + MINIFIED_SCRIPT, mode='w', encoding='utf-8') as fp:
            # Flush the buffer (only perform I/O once).
            fp.write(''.join(content))

        resp = input('\nPush to server? [y|N]: ')
        if resp in ['Y', 'y']:
            resp = input('Username [' + USERNAME + ']:')
            if resp != '':
                USERNAME = resp
            resp = input('Port [' + PORT + ']:')
            if resp != '':
                PORT = resp
            resp = input('Remote destination [' + DEST_REMOTE + ']:')
            if resp != '':
                DEST_REMOTE = resp

            p = subprocess.Popen(['scp', '-P', PORT, DEST_DIR + '/' + MINIFIED_SCRIPT, USERNAME + '@example.com:' + DEST_REMOTE])
            sts = os.waitpid(p.pid, 0)
            print('Minified script ' + MINIFIED_SCRIPT + ' pushed to ' + DEST_REMOTE + ' on remote server.')
        else:
            print('Minified script ' + MINIFIED_SCRIPT + ' created in ' + DEST_DIR + '/')

        print('Done!')

    except (KeyboardInterrupt):
        # Control-c sent a SIGINT to the process, handle it.
        print('\nProcess aborted!')
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
        sys.exit(2)

    main(sys.argv[1:])

