import pickle
import sys
from tqdm import tqdm

data = pickle.load(open("../../data/corpus/code-comment-corpus.pkl", "rb"))
for key, (_, doc) in tqdm(data.items()):
    filename = "__".join([str(k).replace(".", "_") for k in key]) + ".txt"

    with open("../../data/docstrings/{}".format(filename), "w+") as outfile:
        outfile.write(" ".join(doc))
