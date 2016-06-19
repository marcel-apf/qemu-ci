class TestState(object):
    PENDING = 0
    SUCCESS = 1
    WARNING = 2
    FAILURE = 3

class Test(object):
    def __init__(self, name):
        self.name = name
        self.state = None
        self.summary = None
        self.url = None

class Series(object):
    def __init__(self, sid, revision):
        self.sid = sid
        self.revision = revision
        self.mbox_path = None
        self.subject = None
