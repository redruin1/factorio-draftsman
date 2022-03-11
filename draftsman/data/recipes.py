# recipes.py

import pickle


with open("draftsman/data/recipes.pkl", "rb") as inp:
    _data = pickle.load(inp)
    raw = _data[0]
    categories = _data[1]
    for_machine = _data[2]