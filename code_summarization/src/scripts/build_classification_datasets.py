import pickle
import random
import csv

import utils.utils as utils


pos_neg_corpus = utils.CODE_CORPUS / "corpus" / "pos-neg-corpus.pkl"
rand_path = utils.CODE_CORPUS / "input" / "random_classification_dataset.tsv"
challenge_path = utils.CODE_CORPUS / "input" / "challenge_classification_dataset.tsv"
pos_neg_dataset = pickle.load(open(pos_neg_corpus, "rb"))

random_dataset, challenge_dataset = list(), list()
for name, func_dict in pos_neg_dataset.items():
    code = func_dict["code"]
    corr_comm = func_dict["comm"]
    rand_negs = func_dict["random_negs"]
    lucene_negs = func_dict["lucene_negs"]
    random_dataset.append((code, corr_comm, True))
    random_dataset.append((code, rand_negs[0], False))
    challenge_dataset.append((code, corr_comm, True))
    challenge_dataset.append(code, lucene_negs[0], False)


def write_tsv(path, data):
    with open(path, 'wt') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        for (code, comm, label) in data:
            tsv_writer.writerow([int(label), " ".join(code), " ".join(comm)])


random.shuffle(random_dataset)
random.shuffle(challenge_dataset)
write_tsv(rand_path, random_dataset)
write_tsv(challenge_path, challenge_dataset)
