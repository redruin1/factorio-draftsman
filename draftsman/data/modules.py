# modules.py

import pickle


with open("draftsman/data/modules.pkl", "rb") as inp:
    _data = pickle.load(inp)
    raw = _data[0]
    categories = _data[1]