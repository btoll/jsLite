import css_compress
import getopt
import js_compress
import sys
import textwrap

def usage():
    str = '''
        Usage:
        --build_dir    The location where the minified files will be moved, defaults to cwd.
        --css          The location of the CSS files, must be specified.
        --js           The location of the JavaScript source files, must be specified.
        --version, -v  The version of the minified script, must be specified.
    '''
    print(textwrap.dedent(str))

def main(argv):
    build_dir = '.'
    dest_dir = '.'
    src_dir = ''
    version = ''

    try:
        opts, args = getopt.getopt(argv, 'hv:', ['help', 'version=', 'build_dir=', 'css=', 'js='])
    except getopt.GetoptError:
        print('Error: Unrecognized flag.')
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif opt == '--build_dir':
            build_dir = arg
        elif opt == '--css':
            css = arg
        elif opt == '--js':
            js = arg
        elif opt in ('-v', '--version'):
            version = arg

    build(version, js, css, build_dir)

def build(version, js, css, build_dir='.'):
    if not version:
        print('Error: You must provide a version.')
        sys.exit(2)

    if not js:
        print('Error: You must provide the location of the source files.')
        sys.exit(2)

    if not css:
        print('Error: You must provide the location of the source files.')
        sys.exit(2)

    js_compress.compress(version, js, build_dir)
    css_compress.compress(version, css, build_dir)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
        sys.exit(2)

    main(sys.argv[1:])

