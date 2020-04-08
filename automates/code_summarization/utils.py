from pathlib import Path
import pickle
import csv
import os
from torchtext import data
from torchtext import vocab

from sklearn.metrics import f1_score, precision_score, recall_score


CODE_CORPUS = Path(os.environ["CODE_CORPUS"])


def accuracy_score(data):
    """
    Given a set of (predictions, truth labels), return the accuracy of the predictions.

    :param data: [List[Tuple]] -- A list of predictions with truth labels
    :returns:    [Float] -- Accuracy metric of the prediction data
    """
    return 100 * sum([1 if p == t else 0 for p, t in data]) / len(data)


def load_all_data(batch_size, corpus_name):
    """
    This function loads all data necessary for training and evaluation of a
    code/comment classification model. Data is loaded from a TSV file that
    contains all data instances. This file is found in the directory pointed to
    by data_path. Training, dev, and testing sets are created for the model
    using a torchtext BucketIterator that creates batches, indicated by the
    batch_size variable such that the batches have minimal padding. This
    function also loads pretrained word embedding vectors that are located in
    the data_path directory.

    :param batch_size: [int] -- amount of data elements per batch
    :returns: [Tuple] -- (TRAIN set of batches,
                          DEV set of batches,
                          TEST set of batches,
                          code pretrained vectors,
                          docstring pretrained vectors)
    """
    input_path = CODE_CORPUS / "input"
    # Create a field variable for each field that will be in our TSV file
    code_field = data.Field(sequential=True, tokenize=lambda s: s.split(" "),
                            include_lengths=True, use_vocab=True)

    comm_field = data.Field(sequential=True, tokenize=lambda s: s.split(" "),
                            include_lengths=True, use_vocab=True)

    label_field = data.Field(sequential=False, use_vocab=False,
                             pad_token=None, unk_token=None)

    # Used to create a tabular dataset from TSV
    train_val_fields = [
        ("label", label_field),
        ("code", code_field),
        ("comm", comm_field),
    ]

    # Build the large tabular dataset using the defined fields
    tsv_file_path = input_path / "{}_dataset.tsv".format(corpus_name)
    tab_data = data.TabularDataset(str(tsv_file_path), "TSV", train_val_fields)

    # Split the large dataset into TRAIN, DEV, TEST portions
    train_data, dev_data, test_data = tab_data.split(split_ratio=[0.85, 0.05, 0.1])

    # Load the pretrained word embedding vectors
    code_vec_path = input_path / "code-vectors.txt"
    comm_vec_path = input_path / "comm-vectors.txt"
    code_vectors = vocab.Vectors(str(code_vec_path), str(input_path))
    comm_vectors = vocab.Vectors(str(comm_vec_path), str(input_path))

    code_char_vec_path = input_path / "code-char-vectors.txt"
    comm_char_vec_path = input_path / "comm-char-vectors.txt"
    code_char_vectors = vocab.Vectors(str(code_char_vec_path), str(input_path))
    comm_char_vectors = vocab.Vectors(str(comm_char_vec_path), str(input_path))

    # Builds the known word vocab for code and comments from the pretrained vectors
    code_field.build_vocab(train_data, dev_data, test_data, vectors=code_vectors)
    comm_field.build_vocab(train_data, dev_data, test_data, vectors=comm_vectors)
    label_field.build_vocab(train_data, dev_data, test_data)    # Necesary for iterator

    # Creates batched TRAIN, DEV, TEST sets for faster training (uses auto-batching)
    (train, val, test) = data.BucketIterator.splits(
        (train_data, dev_data, test_data),              # tuple of data to batch
        sort_key=lambda x: (len(x.code), len(x.comm)),  # Allows for auto-batching by instance size
        batch_size=batch_size,                          # size of batches (for all three datasets)
        repeat=False,                                   # TODO: fill in this
        shuffle=True                                    # Shuffle after full iteration
    )

    # We need to return the test sets and the field pretrained vectors
    return (
        train, val, test,
        code_vectors,
        comm_vectors,
        code_char_vectors,
        comm_char_vectors
    )


def load_generation_data():
    """
    This function loads all data necessary for training and evaluation of a
    code/comment generation model. Data is loaded from a TSV file that
    contains all data instances. This file is found in the directory pointed to
    by data_path. Training, dev, and testing sets are created for the model
    using a torchtext BucketIterator that creates batches, indicated by the
    batch_size variable such that the batches have minimal padding. This
    function also loads pretrained word embedding vectors that are located in
    the data_path directory.

    :param batch_size: [int] -- amount of data elements per batch
    :returns: [Tuple] -- (TRAIN set of batches,
                          DEV set of batches,
                          TEST set of batches,
                          code pretrained vectors,
                          docstring pretrained vectors)
    """
    input_path = CODE_CORPUS / "input"
    # Create a field variable for each field that will be in our TSV file
    code_field = data.Field(sequential=True, tokenize=lambda s: s.split(" "),
                            include_lengths=True, use_vocab=True)

    comm_field = data.Field(sequential=True, tokenize=lambda s: s.split(" "),
                            include_lengths=True, use_vocab=True)

    # Used to create a tabular dataset from TSV
    train_val_fields = [("code", code_field), ("comm", comm_field)]

    # Build the large tabular dataset using the defined fields
    tsv_file_path = input_path / "generation_dataset.tsv"
    tab_data = data.TabularDataset(str(tsv_file_path), "TSV", train_val_fields)

    # Split the large dataset into TRAIN, DEV, TEST portions
    train_data, dev_data, test_data = tab_data.split(split_ratio=[0.85, 0.05, 0.1])

    # Load the pretrained word embedding vectors
    code_vec_path = input_path / "code-vectors.txt"
    comm_vec_path = input_path / "comm-vectors.txt"
    code_vectors = vocab.Vectors(str(code_vec_path), str(input_path))
    comm_vectors = vocab.Vectors(str(comm_vec_path), str(input_path))

    # Builds the known word vocab for code and comments from the pretrained vectors
    code_field.build_vocab(train_data, dev_data, test_data, vectors=code_vectors)
    comm_field.build_vocab(train_data, dev_data, test_data, vectors=comm_vectors)

    # We need to return the test sets and the field pretrained vectors
    return (train_data, dev_data, test_data,
            code_field.vocab, comm_field.vocab)


def save_translations(pairs, filepath):
    """Saves a set of generated translations."""
    (code, truths, translations) = map(list, zip(*pairs))

    with open(filepath + "_code.txt", "w") as outfile:
        for c in code:
            outfile.write(f"{' '.join(c)}\n")

    with open(filepath + "_truth.txt", "w") as outfile:
        for truth in truths:
            outfile.write(f"{' '.join(truth)}\n")

    with open(filepath + "_trans.txt", "w") as outfile:
        for trans in translations:
            outfile.write(f"{' '.join(trans)}\n")


def save_scores(s, filepath):
    """Saves a set of classifications."""
    pickle.dump(s, open(str(filepath), "wb"))


def score_classifier(data):
    """Computes and prints the precision/recall/F1 scores from a set of predictions."""
    preds, truth = map(list, zip(*data))
    p = precision_score(truth, preds)
    r = recall_score(truth, preds)
    f1 = f1_score(truth, preds)
    return p, r, f1
