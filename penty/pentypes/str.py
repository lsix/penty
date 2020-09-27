str_iterator = type(iter(""))

def iterator(self_types):
    result_types = set()
    for o in self_types:
        if o is str:
            result_types.add(str_iterator)
        elif isinstance(o, str):
            result_types.add(str_iterator)
        else:
            raise NotImplementedError
    return result_types