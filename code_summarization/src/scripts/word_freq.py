import pickle
import sys

from utils.utils import CODE_CORPUS


min_freq = int(sys.argv[1])
code_path = CODE_CORPUS / "corpus" / "code-comment-corpus.pkl"
code_data = pickle.load(open(code_path, "rb"))
words = [word for code, comm in code_data.values() for word in code]
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
    else:
        break
below_min = sum([1 for c, w in sorted_counts if c <= min_freq])
print(below_min)
print(len(word_counts.keys()))
