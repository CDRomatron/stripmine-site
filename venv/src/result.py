import json
from flask.json import JSONEncoder

class Result(dict):
    def __init__(self, text, type, id, parentid, metadata):
        dict.__init__(self, text=text, type=type, id=id, parentid=parentid, metadata=metadata)

