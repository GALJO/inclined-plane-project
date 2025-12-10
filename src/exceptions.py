class InputParsingError(Exception):
    def __init__(self, _desc: str):
        self.desc = _desc
        self.code = "Inp.Par"
