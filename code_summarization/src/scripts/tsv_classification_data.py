import csv
import pickle

(train, dev, test) = pickle.load(open("../../data/corpus/classification_dataset.pkl", "rb"))

full_dataset = train + dev + test

with open('../../data/input/classification_data.tsv', 'wt') as out_file:
    tsv_writer = csv.writer(out_file, delimiter='\t')
    for (code, comm, label) in full_dataset:
        code_text = " ".join(code)
        comm_text = " ".join(comm)
        tsv_writer.writerow([int(label), code_text, comm_text])

with open('../../data/input/classification_data.tsv', 'rt') as in_file:
    tsv_reader = csv.reader(in_file, delimiter='\t')
    for row in tsv_reader:
        print(len(row))
        print(row)
