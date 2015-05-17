import getopt
import getpass
import os
import shutil
import subprocess
import sys
import tarfile

def usage(level):
	if level == 0:
		print('''Usage: python3 tar_jslite.py [-hv | --help [--version --src_dir --dest_dir]] [VERSION | SOURCE_DIRECTORY | DESTINATION_DIRECTORY]
Try `python3 tar_jslite.py --help' for more information.''')

	elif level == 1:
		print('''Usage:
  -h, --help		help
  -v, --version		the version of the minified script, must be specified
  --src_dir		the location of the JSLITE source files, defaults to '/usr/local/www/public/dev/jslite/lib/js/'
  --dest_dir		the location where the minified file will be moved, defaults to 'tarballs/\'
        ''')

def main(argv):
	SRC_DIR = "/path/to/src/"
	DEST_DIR = "tarballs"

	try:
		opts, args = getopt.getopt(argv, "hv:", ["help", "version=", "src_dir=", "dest_dir="])
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
	TARBALL = "JSLITE_" + VERSION + ".tgz"
	TMP_DIR = "jslite/"
	PORT = "22"
	DEST_REMOTE = "/path/to/destination/"
	USERNAME = getpass.getuser()

	try:
		shutil.copytree(SRC_DIR, TMP_DIR, ignore=shutil.ignore_patterns("a*", "_*"))
		tar = tarfile.open(DEST_DIR + "/" + TARBALL, "w:gz")
		print("creating new tarball...")

		for file in os.listdir(TMP_DIR):
			tar.add(TMP_DIR + file)
		tar.close()

		print("created new tarball " + TARBALL + " in " + DEST_DIR + "/")
		print("cleaning up...")
		shutil.rmtree(TMP_DIR)

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

			p = subprocess.Popen(["scp", "-P", PORT, DEST_DIR + "/" + TARBALL, USERNAME + "@example.com:" + DEST_REMOTE])
			sts = os.waitpid(p.pid, 0)
			print("tarball " + TARBALL + " pushed to " + DEST_REMOTE + " on remote server")
		else:
			print("tarball " + TARBALL + " created in " + DEST_DIR + "/")

		print("done")

	except (KeyboardInterrupt):
		#control-c sent a SIGINT to the process, handle it
		print("\nprocess aborted")

		#if aborted at input() then TMP_DIR would have already been removed so first check for its existence
		if (os.path.isdir(TMP_DIR)):
			print("cleaning up...")
			shutil.rmtree(TMP_DIR)
			print("done")
		sys.exit(1)

if __name__ == "__main__":
	if len(sys.argv) == 1:
		usage(0)
		sys.exit(2)

	main(sys.argv[1:])

