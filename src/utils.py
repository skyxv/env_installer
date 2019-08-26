class ColorfulOutput:
    OK = '\033[96m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'

    @classmethod
    def ok(cls, info):
        print(cls.OK + info + cls.END)

    @classmethod
    def warning(cls, info):
        print(cls.WARNING + info + cls.END)

    @classmethod
    def fail(cls, info):
        print(cls.FAIL + info + cls.END)

