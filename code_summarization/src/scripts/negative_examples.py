from copy import deepcopy
import random
import pickle
import sys

from tqdm import tqdm
import numpy as np


code_comm_data = pickle.load(open("../../data/corpus/code-comment-corpus.pkl", "rb"))
full_dataset = dict()

data_pair_keys = list(code_comm_data.keys())
shuffled_keys = ["{}-{}".format(path, l_num) for path, l_num in deepcopy(data_pair_keys)]
random.shuffle(shuffled_keys)

for key in tqdm(data_pair_keys, desc="Finding negs"):
    key_string = "{}-{}".format(key[0], key[1])
    shuffled_keys.remove(key_string)
    positive_example = code_comm_data[key]
    # print(shuffled_keys)
    chosen_keys = np.random.choice(np.array(shuffled_keys), size=10, replace=False)
    split_chosen_keys = [k.split("-") for k in chosen_keys]
    corrected_chosen_keys = [(p, int(l)) for p, l in split_chosen_keys]
    # print(chosen_keys)
    # print(corrected_chosen_keys)
    # sys.exit()
    negative_examples = [code_comm_data[k][1] for k in corrected_chosen_keys]
    full_dataset[key] = {
        "code": positive_example[0],
        "comm": positive_example[1],
        "negs": negative_examples
    }
    index = random.randint(0, len(data_pair_keys) - 1)
    shuffled_keys.insert(index, key_string)

pickle.dump(full_dataset, open("../../data/corpus/pos-neg-corpus.pkl", "wb"))
