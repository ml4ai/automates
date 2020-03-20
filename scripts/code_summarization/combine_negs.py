import pickle
from tqdm import tqdm

import utils.utils as utils

pos_neg_corpus = utils.CODE_CORPUS / "corpus" / "pos-neg-corpus.pkl"
challenge_neg_corpus = utils.CODE_CORPUS / "corpus" / "challenge-comms.pkl"
code_comm_corpus = utils.CODE_CORPUS / "corpus" / "code-comment-corpus.pkl"

pos_neg_dataset = pickle.load(open(pos_neg_corpus, "rb"))
challenge_neg_dataset = pickle.load(open(challenge_neg_corpus, "rb"))
code_comm_dataset = pickle.load(open(code_comm_corpus, "rb"))

for orig_key, comm_keys in tqdm(challenge_neg_dataset.items(), desc="Checking comms"):
    if orig_key not in pos_neg_dataset:
        raise ValueError("{} not in pos-neg-corpus")
    # else:
    #     print(pos_neg_dataset[orig_key].keys())
    orig_comm = code_comm_dataset[orig_key][1]
    orig_comm_str = " ".join(orig_comm)
    challenge_negatives = list()
    for comm_key in comm_keys:
        neg_comm = code_comm_dataset[comm_key][1]
        neg_comm_str = " ".join(neg_comm)
        if orig_comm_str != neg_comm_str:
            challenge_negatives.append(neg_comm)

        if len(challenge_negatives) == 10:
            break

    if len(challenge_negatives) < 10:
        print("Only found {} good negatives for {}".format(len(challenge_negatives), orig_key))
        for comm_key in comm_keys[:10-len(challenge_negatives)]:
            challenge_negatives.append(code_comm_dataset[comm_key][1])

    pos_neg_dataset[orig_key]["lucene_negs"] = challenge_negatives

pickle.dump(pos_neg_dataset, open(pos_neg_corpus, "wb"))
