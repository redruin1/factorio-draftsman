# items.py

import pickle


with open("draftsman/data/items.pkl", "rb") as inp:
    _data = pickle.load(inp)
    all = _data[0]
    subgroups = _data[1]
    groups = _data[2]
