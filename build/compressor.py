'''
NOTE JSLITE.prototype.js and then JSLITE.js MUST be compiled first!
- extract only those files that don't match the aforementiond and concat the aforementioned to the front of the stack before iterating
- use os.path.basename to only get the filename
'''

import getopt
import getpass
import glob
import os
import subprocess
import sys
import time

def usage(level):
	if level == 0:
		print('''Usage: python3 compressed.py [-hv | --help [--version --jar --src_dir --dest_dir]] [VERSION | JAR_FILE | SOURCE_DIRECTORY | DESTINATION_DIRECTORY]
Try `python3 compressed.py --help' for more information.''')

	elif level == 1:
		print('''Usage:
  -h, --help		help
  -v, --version		the version of the minified script, must be specified
  --jar			the location of the jar file, defaults to '/usr/local/yuicompressor-2.4.2/build/yuicompressor-2.4.2.jar'
  --src_dir		the location of the JSLITE source files, defaults to '/usr/local/www/public/dev/jslite/lib/js/'
  --dest_dir		the location where the minified file will be moved, defaults to 'yuicompressed/\'
        ''')

def main(argv):
	JAR_FILE = "/path/to/yuicompressor-2.4.2/build/yuicompressor-2.4.2.jar"
	SRC_DIR = "/path/to/src/js/"
	DEST_DIR = "."

	try:
		opts, args = getopt.getopt(argv, "hv:", ["help", "version=", "jar=", "src_dir=", "dest_dir="])
	except getopt.GetoptError:
		usage(0)
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage(1)
			sys.exit(0)
		elif opt in ("-v", "--version"):
			VERSION = arg
		elif opt == "--jar":
			JAR_FILE = arg
		elif opt == "--src_dir":
			SRC_DIR = arg
		elif opt == "--dest_dir":
			DEST_DIR = arg

	#define some constants
	FIRST_IN_FILES = ["JSLITE.prototype.js", "JSLITE.js"]
	MINIFIED_SCRIPT = "JSLITE_" + VERSION + ".min.js"
	COPYRIGHT = '''/*
 	* jsLite
 	*
 	* Copyright (c) 2009 - 2015 Benjamin Toll (benjamintoll.com)
 	* Dual licensed under the MIT (MIT-LICENSE.txt)
 	* and GPL (GPL-LICENSE.txt) licenses.
 	*
 	*/
	'''
	PORT = "22"
	DEST_REMOTE = "/path/to/dir"
	USERNAME = getpass.getuser()

	try:
		print("creating minified script...\n")
		content = [COPYRIGHT] #write to a buffer

		genny = (FIRST_IN_FILES + [os.path.basename(filepath) for filepath in glob.glob(SRC_DIR + "JSLITE*.js") if os.path.basename(filepath) not in FIRST_IN_FILES])

		if len(genny) == 2:
			print("OPERATION ABORTED: No JSLITE source files were found in the specified source directory. Check your path?")
			sys.exit(1)

		for script in genny:
			begin = int(time.time())
			content.append(subprocess.getoutput("java -jar " + JAR_FILE + " " + SRC_DIR + script))
			end = int(time.time())
			print("script " + script + " minified in " + str(end - begin) + "s")

		#this will overwrite pre-existing
		with open(DEST_DIR + "/" + MINIFIED_SCRIPT, mode="w", encoding="utf-8") as fp:
			fp.write("".join(content)) #flush the buffer (only perform I/O once)

		resp = input("Push to server? [Y|n]:")
		if resp in ["Y", "y"]:
			resp = input("Username [" + USERNAME + "]:")
			if resp != "":
				USERNAME = resp
			resp = input("Port [" + PORT + "]:")
			if resp != "":
				PORT = resp
			resp = input("Remote destination [" + DEST_REMOTE + "]:")
			if resp != "":
				DEST_REMOTE = resp

			p = subprocess.Popen(["scp", "-P", PORT, DEST_DIR + "/" + MINIFIED_SCRIPT, USERNAME + "@example.com:" + DEST_REMOTE])
			sts = os.waitpid(p.pid, 0)
			print("minified script " + MINIFIED_SCRIPT + " pushed to " + DEST_REMOTE + " on remote server")
		else:
			print("minified script " + MINIFIED_SCRIPT + " created in " + DEST_DIR + "/")

		print("done")

	except (KeyboardInterrupt):
		#control-c sent a SIGINT to the process, handle it
		print("\nprocess aborted")
		sys.exit(1)

if __name__ == "__main__":
	if len(sys.argv) == 1:
		usage(0)
		sys.exit(2)

	main(sys.argv[1:])

