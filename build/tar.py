import getopt
import getpass
import os
import shutil
import subprocess
import sys
import tarfile
import textwrap

def usage():
    str = '''
        Usage:
        --dest_dir     The location where the minified file will be moved, defaults to cwd.
        --src_dir      The location of the JSLITE source files, must be specified.
        --version, -v  The version of the minified script, must be specified.
    '''
    print(textwrap.dedent(str))

def main(argv):
    DEST_DIR = '.'
    SRC_DIR = ''
    VERSION = ''

    try:
        opts, args = getopt.getopt(argv, 'hv:', ['help', 'version=', 'src_dir=', 'dest_dir='])
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
        elif opt == '--src_dir':
            SRC_DIR = arg
        elif opt == '--dest_dir':
            DEST_DIR = arg

    if not SRC_DIR:
        print('Error: You must provide the location of the source files.')
        sys.exit(2)

    if not VERSION:
        print('Error: You must provide a version.')
        sys.exit(2)

    # Define some constants.
    TARBALL = 'JSLITE_' + VERSION + '.tgz'
    TMP_DIR = 'jslite/'
    PORT = '22'
    DEST_REMOTE = '~'
    USERNAME = getpass.getuser()

    try:
        shutil.copytree(SRC_DIR, TMP_DIR, ignore=shutil.ignore_patterns('a*', '_*'))
        tar = tarfile.open(DEST_DIR + '/' + TARBALL, 'w:gz')
        print('Creating new tarball...')

        for file in os.listdir(TMP_DIR):
            tar.add(TMP_DIR + file)

        tar.close()

        print('Created new tarball ' + TARBALL + ' in ' + DEST_DIR + '/')
        print('Cleaning up...')
        shutil.rmtree(TMP_DIR)

        resp = input('Push to server? [y|N]:')
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

            p = subprocess.Popen(['scp', '-P', PORT, DEST_DIR + '/' + TARBALL, USERNAME + '@example.com:' + DEST_REMOTE])
            sts = os.waitpid(p.pid, 0)
            print('Tarball ' + TARBALL + ' pushed to ' + DEST_REMOTE + ' on remote server.')
        else:
            print('Tarball ' + TARBALL + ' created in ' + DEST_DIR + '/')

        print('Done!')

    except (KeyboardInterrupt):
        # Control-C sent a SIGINT to the process, handle it.
        print('\nProcess aborted!')

        # If aborted at input() then TMP_DIR would have already been removed so first check for its existence.
        if (os.path.isdir(TMP_DIR)):
            print('Cleaning up...')
            shutil.rmtree(TMP_DIR)
            print('Done!')

        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
        sys.exit(2)

    main(sys.argv[1:])

