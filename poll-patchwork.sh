#! /bin/sh

/root/git/patchwork/git-pw/git-pw -C /root/git/qemu/ poll-events  |  /root/workspace/poll-patchwork.py
