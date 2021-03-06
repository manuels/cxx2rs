#!/usr/bin/env python

import os
import glob
import subprocess
import difflib

def diff(fname_cxx, actual_output, expected_output):
	diff_lines = difflib.unified_diff(actual_output, expected_output)

	different = False
	for line in diff_lines:
		if not different:
			print '================ "%s" test FAILED! diff begin ================' % os.path.basename(fname_cxx)
			different = True
		print line

	if different:
		print '================  "%s" test FAILED! diff end  ================' % os.path.basename(fname_cxx)

	return not different


def compile(fname_cxx, fname_rs, fname_run_rs):
	cmd = 'gcc -c %s -o /tmp/libcxx.a' % fname_cxx
	cmd = 'clang -c %s -o /tmp/libcxx.a' % fname_cxx
	print cmd
	print subprocess.check_output(cmd.split())

	cmd = 'rustc -o /tmp/libfoo.rlib %s' % fname_rs
	print cmd
	print subprocess.check_output(cmd.split())

	if fname_run_rs is not None:
		cmd = 'rustc -L /tmp/ %s -o /tmp/main' % fname_run_rs
		print cmd
		print subprocess.check_output(cmd.split())

	success = True


def run_test(fname_cxx):
	fname_run_rs = os.path.splitext(fname_cxx)[0] + "_run.rs"
	if not os.path.exists(fname_run_rs):
		fname_run_rs = None

	fname_rs = os.path.splitext(fname_cxx)[0] + ".rs"
	with open(fname_rs) as f:
		expected_output = f.read().split()

	cmd = ['./cxx2rs.py', 'cxx', fname_cxx]
	actual_output = subprocess.check_output(cmd).split()
	
	success = diff(fname_cxx, actual_output, expected_output)
	print fname_run_rs, success
	
	if success:
		success = compile(fname_cxx, fname_rs, fname_run_rs)

	if success:
		print 'Test "%s" succeeded.' % os.path.basename(fname_cxx)
	else:
		print


def main():
	basepath = os.path.dirname(__file__)
	testpath = os.path.join(basepath, './tests/*.c*')

	for fname_cxx in glob.glob(testpath):
		with open(fname_cxx, 'r') as f:
			first_line = f.readline()

			if first_line.lower().strip() == '// skip':
				print 'Skipping test "%s".' % os.path.basename(fname_cxx)
				continue

			print 'Running test "%s"...' % os.path.basename(fname_cxx)
			run_test(fname_cxx)

if __name__ == "__main__":
	main()
