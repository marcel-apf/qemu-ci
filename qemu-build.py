#!/bin/env python2
# coding=utf-8
import fileinput
import json
import mailbox
import os
import re
import subprocess
import time
import sys
import shutil
import patchworkq
import commonq

class BuildType(object):
    CHECKPATCH = 0

class Build(object):
    def process_patch(self, mail):
        return false

class CheckpatchBuild(Build):
    CHECKPATCH_PATH = '/root/git/qemu/scripts/checkpatch.pl'

    def __init__(self, build_number):
        self.build_number = build_number
        self.summary = 'Summary: '

    def _counts(self, results):
        counts = [0, 0]
        error = re.compile(r'^ERROR:')
        warning = re.compile(r'^WARNING')
        lines = results.splitlines()
        if lines:
            for line in iter(lines):
                if error.search(line):
                    counts[0] += 1
                elif warning.search(line):
                    counts[1] += 1
        return counts

    def process_patch(self, mail):
        subject = mail.get('Subject').replace('\n', '')
        print 'Testing %s\n' % subject

        cmd = subprocess.Popen([self.CHECKPATCH_PATH,
                                '--no-summary', '--mailback', '-'],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        (stdout, _) = cmd.communicate(input=mail.as_string())
        (n_errors, n_warnings) = self._counts(stdout)
        if  n_errors > 0 or n_warnings > 0:
            self.summary +=  subject + ': ===> [' + str(n_errors) + ' errors / ' + str(n_warnings) + '  warnings];'
        print stdout
        return  n_errors == 0

class BuildRunner(object):
    def _process_mbox_file(self, build_type, build_number, mbox_file):
        if build_type == BuildType.CHECKPATCH:
            test = CheckpatchBuild(build_number)
        else:
            print "Unknown build type: " + str(build_type) + '!'
            return False

        result = True
        for mail in mailbox.mbox(mbox_file):
            result &= test.process_patch(mail)

        print test.summary
        return result

    def run(self):
        if len(sys.argv) < 6:
            print 'Usage qemu-build.py build_type build-number /path/to/mbox series_id series_revision'
            sys.exit(1)
        build_type = int(sys.argv[1])
        build_number = int(sys.argv[2])
        series = commonq.Series(int(sys.argv[4]), sys.argv[5])
        series.mbox_path = sys.argv[3]

        if not os.path.isfile(series.mbox_path):
            print series.mbox_path + "can't be found"
            sys.exit(1)

        success =  self._process_mbox_file(build_type, build_number, series.mbox_path)

        if not success:
            sys.exit(1)

if __name__ == '__main__':
    runner = BuildRunner()
    runner.run()
