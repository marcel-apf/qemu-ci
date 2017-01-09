#!/bin/env python2
# coding=utf-8
import json
import requests
import jenkins
import pprint
import time
import commonq

JENKINS_URL = 'http://localhost:8080'
JENKINS_USERNAME = 'admin'
JENKINS_PASSWORD = '12345'

class JenkinsBuild(object):
    def __init__(self, project_name, series):
        self.project_name = project_name
        self.series = series

        self.server = jenkins.Jenkins(JENKINS_URL,
                                      username = JENKINS_USERNAME,
                                      password = JENKINS_PASSWORD)
        self.build = None

    def debug(self):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.build)

    def start(self):
        next_build_number = self.server.get_job_info(self.project_name)['nextBuildNumber']
        output = self.server.build_job(self.project_name,
                                       {
                                         'series_subject':  self.series.subject,
                                         'series_id':       self.series.sid,
                                         'series_revision': self.series.revision
                                       })
        while self.build == None:
            time.sleep(1)
            builds = self.server.get_job_info(self.project_name)['builds']
            for b in builds:
                b_num = b['number']
                if b_num < next_build_number:
                    continue;
                build_info = self.server.get_build_info(self.project_name,
                                                        b_num)
                build_actions = build_info['actions']
                for build_action in build_actions:
                    if not build_action.has_key('parameters'):
                        continue;
                    build_parameters = build_action.get('parameters')
                    for build_parameter in build_parameters:
                        if not build_parameter.get('name') == 'series_id':
                            continue;
                        if int(build_parameter.get('value')) == self.series.sid:
                            self.build = build_info
                            break;

    def wait(self):
        while not self.build['result']:
            time.sleep(5)
            self.build = self.server.get_build_info(self.project_name,
                                                    self.build['number'])

    def succeded(self):
        return self.build['result'] == 'SUCCESS'

    def description(self):
        return str(self.build['description']).replace(';','\n')

    def url(self):
        return self.build['url'] + 'console'

