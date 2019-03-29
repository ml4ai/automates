import sys
import numpy as np
from nltk.translate.bleu_score import sentence_bleu

references = list()
with open(sys.argv[1], "r") as reference_file:
    for line in reference_file.readlines():
        references.append(line.strip().split(" "))

translations = list()
with open(sys.argv[2], "r") as translation_file:
    for line in translation_file.readlines():
        translations.append(line.strip().split(" "))

scores = list()
for reference, translation in zip(references, translations):
    scores.append(sentence_bleu([reference], translation, weights=(0.5, 0.5)))

print(f"Average BLEU score: {np.mean(scores)}")
