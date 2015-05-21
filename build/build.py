import css_compress
import getopt
import js_compress
import sys
import textwrap

def usage():
    str = '''
        Usage:
        --build_dir        The location where the minified files will be moved, defaults to cwd.
        --css_src          The location of the CSS files, must be specified.
        --js_src           The location of the JavaScript source files, must be specified.
        --version, -v      The version of the minified script, must be specified.
    '''
    print(textwrap.dedent(str))

def main(argv):
    build_dir = '.'
    css_src = ''
    js_src = ''
    version = ''

    try:
        opts, args = getopt.getopt(argv, 'hv:', ['help', 'version=', 'build_dir=', 'css_src=', 'js_src='])
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
        elif opt == '--css_src':
            css_src = arg
        elif opt == '--js_src':
            js_src = arg
        elif opt in ('-v', '--version'):
            version = arg

    build(version, js_src, css_src, build_dir)

def build(version, js_src, css_src, build_dir='.'):
    if not version:
        print('Error: You must provide a version.')
        sys.exit(2)

    if not js_src:
        print('Error: You must provide the location of the JavaScript source files.')
        sys.exit(2)

    if not css_src:
        print('Error: You must provide the location of the CSS files.')
        sys.exit(2)

    # The order is very important due to some dependencies between scripts, so specify the dependency order here.
    dependencies = [
        'JSLITE.prototype.js',
        'JSLITE.js',
        'JSLITE.Element.js',
        'JSLITE.Composite.js',
        'JSLITE.Observer.js'
    ]

#    copyright = '''\
#        /*
#         * jsLite {version!s}
#         *
#         * Copyright (c) 2009 - 2015 Benjamin Toll (benjamintoll.com)
#         * Dual licensed under the MIT (MIT-LICENSE.txt)
#         * and GPL (GPL-LICENSE.txt) licenses.
#         *
#         */
#    '''.format(**locals())
#
#    # Write to a buffer.
#    buff = [textwrap.dedent(copyright)]

    js_output = 'JSLITE_' + version + '.min.js'
    css_output = 'JSLITE_CSS_' + version + '.min.js'

    js_compress.compress(version, js_src, js_output, build_dir, dependencies)
    css_compress.compress(version, css_src, css_output, build_dir)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
        sys.exit(2)

    main(sys.argv[1:])

