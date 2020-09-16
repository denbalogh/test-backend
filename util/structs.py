def _sanitize_input(item):
    if type(item) is str:
        return item.strip().lower()
    else:
        return item

class UserInputDict(dict):
    def __init__(self, *arg, **kw):
      super(UserInputDict, self).__init__(*arg, **kw)

    def __getitem__(self, key):
        item = super().__getitem__(key)
        return _sanitize_input(item)

    def get(self, key, default=None, type=None):
        item = super().get(key, default)
        if type is not None:
            item = type(item)
        
        return _sanitize_input(item)

    def get_list(self, key, default=None, type=None):
        item = super().get(key, default)
        if type is None:
            type = str

        try:
            return UserInputList([_sanitize_input(type(e)) for e in item.split(",")])
        except AttributeError:
            return item

class UserInputList(list):
    def __init__(self, *arg, **kw):
      super(UserInputList, self).__init__(*arg, **kw)

    def __contains__(self, key):
        return super().__contains__(_sanitize_input(key))
