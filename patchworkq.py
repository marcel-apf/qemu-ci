#!/bin/env python2
# coding=utf-8
import json
import os
import subprocess
import requests
import tempfile
import commonq

PATCHWORK_URL = 'http://localhost'
API_URL = PATCHWORK_URL + '/api/1.0'
GIT_PW = '/root/git/patchwork/git-pw/git-pw'
QEMU_PATH = '/root/git/qemu'

class PatchworkSeries(commonq.Series):
    state_names = ['pending', 'success', 'warning', 'failure']

    def __init__(self, sid, revision):
        commonq.Series.__init__(self, sid, revision)

    def _query_mbox_path(self):
        mbox_url = API_URL + ('/series/%d/revisions/%d/mbox/' %
                              (self.sid, self.revision))
        r = requests.get(mbox_url)

        fd, self.mbox_path = tempfile.mkstemp()
        with os.fdopen(fd, 'w+') as tmp:
            tmp.write(r.content)
        os.chmod(self.mbox_path, 0555)

    def _query_subject(self):
        series_url = API_URL + ('/series/%d/' % self.sid)
        r = requests.get(series_url)
        self.subject = r.json()['name']

    def load(self):
        self._query_mbox_path()
        self._query_subject()

    def post_test_result(self, test):
        cmd = subprocess.Popen([GIT_PW, '-C', QEMU_PATH, 'post-result', str(self.sid),
                                '--revision', str(self.revision),
                                test.name, self.state_names[test.state],
                                '--summary', test.summary,
                                '--url', test.url])
        cmd.wait();


