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
import git



class BuildType(object):
    CHECKPATCH = 0
    GIT_AM = 1

class GitAmBuild(object):
    QEMU_PATH = '/root/git/qemu'

    def __init__(self, build_number):
        self.build_number = build_number
        self.summary = 'Summary: '
        self.repo = git.Repo(self.QEMU_PATH)

    """ 'Borrowed' from https://git.samba.org/, hg-fast-export.py"""
    def _sanitize_name(self, name):
        """Sanitize input roughly according to git-check-ref-format"""
        def _dot(name):
            if name[0] == '.': return '_'+name[1:]
            return name

        n = name
        p = re.compile('([[ ^:?*]|\.\.)')
        n = p.sub('_', n)
        if n[-1] == '/':
            n=n[:-1]+'_'
        n = '/'.join(map(_dot,n.split('/')))
        p = re.compile('_+')
        n = p.sub('_', n)

        return n

    def process_series(self, series):

        subject = series.subject
        print 'Commiting %s\n' % subject

        subject += ' ' +  str(series.revision)
        branch = self._sanitize_name(subject)

        self.repo.heads.master.checkout()

        for h in self.repo.heads:
            if h.name == branch:
                self.repo.delete_head(h, '-D')

        head = self.repo.create_head(branch)
        head.checkout()

        (result, output) = series.git_am()

        print output

        if result != 0:
            for line in str(output).split('\n'):
                if str(line).startswith('Patch failed at'):
                    self.summary +=  str(line)
            self.repo.git.am('--abort')

        return result == 0

class CheckpatchBuild(object):
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

    def process_patch(self, patch):
        subject = patch.get('Subject').replace('\n', '')
        print 'Testing %s\n' % subject

        cmd = subprocess.Popen([self.CHECKPATCH_PATH,
                                '--no-summary', '--mailback', '-'],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        (stdout, _) = cmd.communicate(input=patch.as_string())
        (n_errors, n_warnings) = self._counts(stdout)
        if  n_errors > 0 or n_warnings > 0:
            self.summary +=  subject + ': ===> [' + str(n_errors) + ' errors / ' + str(n_warnings) + '  warnings];'
        print stdout
        return  n_errors == 0

class BuildRunner(object):
    def _process_mbox_file(self, build_type, build_number, series):
        if build_type == BuildType.CHECKPATCH:
            test = CheckpatchBuild(build_number)
            result = True
            for mail in mailbox.mbox(series.mbox_path):
                result &= test.process_patch(mail)
        elif build_type == BuildType.GIT_AM:
            test = GitAmBuild(build_number)
            result = test.process_series(series)
        else:
            print "Unknown build type: " + str(build_type) + '!'
            return False

        print test.summary
        return result

    def run(self):
        if len(sys.argv) < 5:
            print 'Usage qemu-build.py build_type build-number series_id series_revision'
            sys.exit(1)
        build_type = int(sys.argv[1])
        build_number = int(sys.argv[2])
        series = patchworkq.PatchworkSeries(int(sys.argv[3]), int(sys.argv[4]))
        series.load()

        if not os.path.isfile(series.mbox_path):
            print series.mbox_path + "can't be found"
            sys.exit(1)

        success =  self._process_mbox_file(build_type, build_number, series)

        if not success:
            sys.exit(1)

if __name__ == '__main__':
    runner = BuildRunner()
    runner.run()
