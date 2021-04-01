import pickle
import sys

from utils.utils import CODE_CORPUS


def get_words(filepath):
    results = list()
    with open(filepath, "r+") as infile:
        for line in infile:
            words = line.split()
            results.extend(words)
    return results


min_freq = int(sys.argv[2])
# data_idx = int(sys.argv[2])
data_path = CODE_CORPUS / "corpus" / sys.argv[1]
words = get_words(data_path)
word_counts = dict()
for word in words:
    if word in word_counts:
        word_counts[word] += 1
    else:
        word_counts[word] = 1

sorted_counts = sorted([count, word] for word, count in word_counts.items())

for c, w in sorted_counts:
    if c <= min_freq:
        print(c, ": ", w)
        try:
            w.encode("utf-8").decode("ascii")
        except UnicodeDecodeError as e:
            print(w, " has unicode!!!")
    else:
        break
min_or_below = sum([1 for c, w in sorted_counts if c <= min_freq])
print(min_or_below)
print(len(word_counts.keys()))
