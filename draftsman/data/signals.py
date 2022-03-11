# signals.py

import pickle


with open("draftsman/data/signals.pkl", "rb") as inp:
    _data = pickle.load(inp)
    raw = _data[0]
    item = _data[1]
    fluid = _data[2]
    virtual = _data[3]
    