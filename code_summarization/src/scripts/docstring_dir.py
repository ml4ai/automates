import pickle
import sys
from tqdm import tqdm

import utils.utils as utils

code_comm_corpus_path = utils.CODE_CORPUS / "corpus" / "code-comment-corpus.pkl"
data = pickle.load(open(code_comm_corpus_path, "rb"))
base_path = "/Users/phein/Documents/repos/pylucene_example/docstrings"
for key, (_, doc) in tqdm(data.items()):
    filename = "__".join([str(k).replace(".", "_") for k in key]) + ".txt"

    with open("{}/{}".format(base_path, filename), "w+") as outfile:
        outfile.write(" ".join(doc))
