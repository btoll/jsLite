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
    dest_dir = '.'
    src_dir = ''
    version = ''

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
            version = arg
        elif opt == '--src_dir':
            src_dir = arg
        elif opt == '--dest_dir':
            dest_dir = arg

    tar(version, src_dir, dest_dir)

def tar(version, src_dir, dest_dir='.'):
    if not version:
        print('Error: You must provide a version.')
        sys.exit(2)

    if not src_dir:
        print('Error: You must provide the location of the source files.')
        sys.exit(2)

    # Define some constants.
    tarball = 'JSLITE_' + version + '.tgz'
    tmp_dir = 'jslite/'
    port = '22'
    dest_remote = '~'
    username = getpass.getuser()

    try:
        shutil.copytree(src_dir, tmp_dir, ignore=shutil.ignore_patterns('a*', '_*'))
        tar_object = tarfile.open(dest_dir + '/' + tarball, 'w:gz')
        print('Creating new tarball...')

        for file in os.listdir(tmp_dir):
            tar_object.add(tmp_dir + file)

        tar_object.close()

        print('Created new tarball ' + tarball + ' in ' + dest_dir + '/')
        print('Cleaning up...')
        shutil.rmtree(tmp_dir)

        resp = input('Push to server? [y|N]:')
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

            p = subprocess.Popen(['scp', '-P', port, dest_dir + '/' + tarball, username + '@example.com:' + dest_remote])
            sts = os.waitpid(p.pid, 0)
            print('Tarball ' + tarball + ' pushed to ' + dest_remote + ' on remote server.')
        else:
            print('Created tarball ' + tarball + ' in ' + dest_dir + '/')

    except (KeyboardInterrupt):
        # Control-C sent a SIGINT to the process, handle it.
        print('\nProcess aborted!')

        # If aborted at input() then tmp_dir would have already been removed so first check for its existence.
        if (os.path.isdir(tmp_dir)):
            print('Cleaning up...')
            shutil.rmtree(tmp_dir)
            print('Done!')

        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
        sys.exit(2)

    main(sys.argv[1:])

