#!/bin/env python2
# coding=utf-8
import fileinput
import json
import mailbox
import requests
import pprint
import time
import jenkinsq
import patchworkq
import commonq

class GitAmTest(commonq.Test):
    def __init__(self):
        commonq.Test.__init__(self, 'git-am')
        self.build = None

    def process_patch(self, series):
        self.build = jenkinsq.JenkinsBuild('QEMU-git-am', series)
        self.build.start()
        self.build.wait()

        self.state = commonq.TestState.SUCCESS if self.build.succeded() else commonq.TestState.FAILURE
        self.summary = self.build.description()
        self.url = self.build.url()

class CheckpatchTest(commonq.Test):
    def __init__(self):
        commonq.Test.__init__(self, 'checkpatch')
        self.build = None

    def process_patch(self, series):
        self.build = jenkinsq.JenkinsBuild('QEMU-checkpatch', series)
        self.build.start()
        self.build.wait()

        self.state = commonq.TestState.SUCCESS if self.build.succeded() else commonq.TestState.WARNING
        self.summary = self.build.description()
        self.url = self.build.url()

class TestRunner(object):
    def _process_event(self, event):
        sid = event['series']
        revision = event['parameters']['revision']

        series_pw = patchworkq.PatchworkSeries(sid, revision)
        series_pw.load();

        test = CheckpatchTest()
        print('== Running %s on series %d v%d' % (test.name, sid, revision))
        test.process_patch(series_pw)
        series_pw.post_test_result(test)

        test = GitAmTest()
        print('== Running %s on series %d v%d' % (test.name, sid, revision))
        test.process_patch(series_pw)
        series_pw.post_test_result(test)

    def run(self):
        for line in fileinput.input():
            self._process_event(json.loads(line))

if __name__ == '__main__':
    runner = TestRunner()
    runner.run()




#        pp = pprint.PrettyPrinter(indent=4)
#        pp.pprint(event)


