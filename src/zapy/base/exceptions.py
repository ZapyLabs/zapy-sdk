class HandledException(Exception):
    pass


class ZapyException(Exception):
    namespace: str
    identifier: str
    context: dict

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = dict()

    @property
    def error_type(self):
        return f"{self.namespace}:{self.identifier}"
