import nltk
import sys
import numpy as np

references = list()
with open(sys.argv[1], "r") as reference_file:
    for line in reference_file.readlines():
        references.append(line.strip().split(" "))
trans_file_name = sys.argv[2]
translations = list()
with open(trans_file_name, "r") as translation_file:
    for line in translation_file.readlines():
        translations.append(line.strip().split(" "))

scores = list()
for reference, translation in zip(references, translations):
    bleu_score = nltk.translate.bleu_score.sentence_bleu([reference], translation, weights = (0.5, 0.5))
    scores.append(bleu_score)

print("Average BLEU score for {}: {}".format(trans_file_name[:-3], np.mean(scores)))
