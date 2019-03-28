import pickle
import random
import csv
from tqdm import tqdm

import utils.utils as utils


pos_neg_corpus = utils.CODE_CORPUS / "corpus" / "pos-neg-corpus.pkl"
rand_path = utils.CODE_CORPUS / "input" / "random_draw_dataset.tsv"
challenge_path = utils.CODE_CORPUS / "input" / "challenge_dataset.tsv"
pos_neg_dataset = pickle.load(open(pos_neg_corpus, "rb"))

random_dataset, challenge_dataset = list(), list()
for name, func_dict in tqdm(pos_neg_dataset.items(), desc="Creating Datasets"):
    code = func_dict["code"]
    corr_comm = func_dict["comm"]
    rand_negs = func_dict["random_negs"]

    random_dataset.append((1, code, corr_comm))
    for neg in rand_negs:
        random_dataset.append((0, code, neg))

    lucene_negs = func_dict["lucene_negs"]
    challenge_dataset.append((1, code, corr_comm))
    for neg in lucene_negs:
        challenge_dataset.append((0, code, neg))


def write_tsv(path, data):
    with open(path, 'wt') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        tsv_writer.writerows(data)


random.shuffle(random_dataset)
random.shuffle(challenge_dataset)
write_tsv(rand_path, random_dataset)
write_tsv(challenge_path, challenge_dataset)
