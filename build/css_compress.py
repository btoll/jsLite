import getopt
import getpass
import glob
import os
import re
import subprocess
import sys
import textwrap
import time

def usage():
    str = '''
        Usage:
        --dest_dir      The location where the minified file will be moved, defaults to cwd.
        --src_dir       The location of the JSLITE source files, defaults to '/usr/local/www/public/dev/jslite/lib/js/'.
        --version, -v   The version of the minified script, must be specified.
    '''
    print(textwrap.dedent(str))

def main(argv):
    dest_dir = '.'
    src_dir = ''
    version = ''

    try:
        opts, args = getopt.getopt(argv, 'hj:v:', ['help', 'version=', 'src_dir=', 'dest_dir='])
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

    if not src_dir:
        print('Error: You must provide the location of the source files.')
        sys.exit(2)

    if not version:
        print('Error: You must provide a version.')
        sys.exit(2)

    compress(version, src_dir, dest_dir)

def compress(version, src_dir, dest_dir='.'):
    # The order is very important due to some dependencies between scripts, so specify the dependency order here.
    #FIRST_IN_FILES = []

    minified_script = 'JSLITE_CSS_' + version + '.min.js'
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
        content = [textwrap.dedent(copyright)]

        genny = ([os.path.basename(filepath) for filepath in glob.glob(src_dir + '*.css') if os.path.basename(filepath)])

        if not len(genny):
            print('OPERATION ABORTED: No CSS files were found in the specified source directory. Check your path?')
            sys.exit(1)

        def replace_match(match_obj):
            if not match_obj.group(1) == '':
                return match_obj.group(1)
            else:
                return ''

        # Strip out any comments of the "/* ... */" type (non-greedy). The subexpression matches all chars AND whitespace.
        reStripComments = re.compile(r'/\*(?:.|\s)*?\*/')
        # Remove all whitespace before and after the following chars: { } : ; = , < >
        reRemoveWhitespace = re.compile(r'\s*({|}|:|;|=|,|<|>)\s*')
        # Lastly, replace all double spaces with a single space.
        reReplaceDoubleSpaces = re.compile(r'^\s+|\s+$')

        for script in genny:
            with open(src_dir + script) as f:
                file_contents = f.read()

            file_contents = reStripComments.sub('', file_contents)
            file_contents = reRemoveWhitespace.sub(replace_match, file_contents)
            file_contents = reReplaceDoubleSpaces.sub('', file_contents)

            content.append(file_contents)
            print('CSS file ' + script + ' minified.')

        # This will overwrite pre-existing.
        with open(dest_dir + '/' + minified_script, mode='w', encoding='utf-8') as fp:
            # Flush the buffer (only perform I/O once).
            fp.write(''.join(content))

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
            print('Minified file ' + minified_script + ' pushed to ' + dest_remote + ' on remote server.')
        else:
            print('Minified file ' + minified_script + ' created in ' + dest_dir + '/')

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

