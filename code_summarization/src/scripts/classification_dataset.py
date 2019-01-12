import pickle
import random


pos_neg_dataset = pickle.load(open("../../data/corpus/pos-neg-corpus.pkl", "rb"))
full_dataset = list()
for name, func_dict in pos_neg_dataset.items():
    code = func_dict["code"]
    corr_comm = func_dict["comm"]
    negs = func_dict["negs"]
    full_dataset.append((code, corr_comm, True))
    full_dataset.append((code, negs[0], False))
    # for comm in negative_examples:
    #     full_dataset.append((code, comm, False))

random.shuffle(full_dataset)
print("The dataset has {} elements".format(len(full_dataset)))

# NOTE hard coding split values for now
train_dataset = full_dataset[:40000]
dev_dataset = full_dataset[40000:42000]
test_dataset = full_dataset[42000:]

print("Number of elements in each set: (TRAIN={}, DEV={}, TEST={})".format(len(train_dataset), len(dev_dataset), len(test_dataset)))

pickle.dump((train_dataset, dev_dataset, test_dataset),
            open("../../data/corpus/classification_dataset.pkl", "wb"))
