import pickle
import sys

from tqdm import tqdm

import utils.utils as utils

code_path = utils.CODE_CORPUS / "corpus" / "code-comment-corpus.pkl"
code_data = pickle.load(open(code_path, "rb"))

clean_comments = dict()
for key, (code, comm) in tqdm(code_data.items(), desc="Cleaning"):
    comm_str = " ".join(comm)
    clean_comm = comm_str.replace("*", "STAR").replace("/", "DIV") \
                         .replace("+", "PLUS").replace("-", "SUB") \
                         .replace("?", "QUE").replace("\\", "SLSH") \
                         .replace("`", "BTCK").replace("'", "TCK") \
                         .replace("(", "LPAR").replace(")", "RPAR") \
                         .replace("[", "LBKT").replace("]", "RBKT") \
                         .replace("{", "LCRL").replace("}", "RCRL") \
                         .replace("|", "BAR").replace("!", "BNG") \
                         .replace(":", "CLN").replace(";", "SCLN") \
                         .replace("\"", "QTE").replace("=", "EQ") \
                         .replace("<", "LCAR").replace(">", "RCAR") \
                         .replace("@", "ATS").replace("#", "PND") \
                         .replace("$", "DLR").replace("%", "PRCT") \
                         .replace("^", "CAR").replace("&", "AMP") \
                         .replace("~", "TLD")
    clean_comments[key] = clean_comm.split()

comm_path = utils.CODE_CORPUS / "corpus" / "clean-comments.pkl"
pickle.dump(clean_comments, open(comm_path, "wb"))
