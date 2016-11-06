def utf8Dict(d):
    # iterate over the key/values pairings
    for k, v in d.items():
        # if v is a list join and encode else just encode as it is a string
        if isinstance(v, dict):
            utf8Dict(v)
        elif isinstance(v, list):
            utf8List(v)
        else:
            d[k] = v.encode("utf-8")
            print d[k]
    return d

def utf8List(l):
    for i in l:
        if isinstance(i, dict):
            utf8Dict(i)
        elif isinstance(i, list):
            utf8List(i)
        else:
            print i
            i = i.encode("utf-8")
    return l