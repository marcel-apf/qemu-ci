# qemu-ci
A patchwork-jenkins integration attempt to be used for QEMU CI

Intro
=====
The project is nothing more than a set of scripts used to integrate patchwork and jenkins.
I am using https://github.com/dlespiau/patchwork.git project (because it has series support) and Jenkins 1.625.3.
It doesn't have to be used only for QEMU, but I am not going to do anyhting generic at this stage.

What it aims to achieve
=======================
We want to be able to run a series of tests on each series, see the results
and be able to pintpoint to the exact failure point.
Patchwork is used as the main UI while Jenknins is used as the build framework
to easily run the tests and keep the results.
Summaries are available on Patchwork, but for details and logs a link to Jenkins
will be provided. Basically each test type matches a Jenkins Project and each
Patchwork series test run is a Jenknins Build.

How it works
============
- A gmail account is connected to QEMU mailing lists.
- Fetchmail is used to provide the mails to patchwork using the patchwork provided parsemail.sh.
  See .fetchmailrc for the configuration.
- A cron script runs every x minutes (*/15 * * * * root poll-patchwork.sh) and
  query new patchwork 'events'. (poll-patchwork.sh is a wrapper to poll-patchwork.py)
- Each event is a revision of a *complete* series and can be received as mbox file using
  the patchwork API. The file patchworkq.py encapsulates the logic.
- For each CI test a new Jenkins project is to be created and have the path to mbox file,
  series id and series revision as parameters.
- The Jenkins project runs a single bash script 'qemu-build.sh' which is a wrapper to 'qemu-build.py'.
  (See exported configuration jenkins-qemu-checkpatch.xml)
- See jenkinsq.py to see how the build is triggered.
- 'poll-patchwork.py' script waits until the build is finished and updates Pathwork with the
  build results.


* I am running everything as root and I shouldn't, but the project is a POC anyway.
* I am new to python, if you see strange constructs feel free to comment and I'll be sure
  to take care of it.
