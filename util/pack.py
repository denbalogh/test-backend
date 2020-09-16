import json
import pickle

MODE = "json"

def dumps(obj):
    """Pack the value of the given parameter using the configured mode"""
    if MODE == "pickle":
        return pickle.dumps(obj)
    elif MODE == "json":
        return json.dumps(obj)
    else:
        return obj


def loads(string):
    """Unpack the value of the given parameter using the configured mode"""
    if string is None or len(string) == 0:
        return string
    elif MODE == "pickle":
        return pickle.loads(string)
    elif MODE == "json":
        return json.loads(string)
    else:
        return string
