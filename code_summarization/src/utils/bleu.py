import sys
import numpy as np
from nltk.translate.bleu_score import sentence_bleu
from utils import CODE_CORPUS


references = list()
ref_path = CODE_CORPUS / "results" / sys.argv[1]
with open(ref_path, "r") as reference_file:
    for line in reference_file.readlines():
        references.append(line.strip().split(" "))

translations = list()
trans_path = CODE_CORPUS / "results" / sys.argv[2]
with open(trans_path, "r") as translation_file:
    for line in translation_file.readlines():
        translations.append(line.strip().split(" "))

scores = list()
for reference, translation in zip(references, translations):
    score = sentence_bleu([reference], translation, weights=(1.0,))
    scores.append((score, reference, translation))

nums = [s for s, _, _ in scores]
print(f"Average BLEU score: {np.mean(nums)}")

scores.sort(key=lambda tup: tup[0], reverse=True)
for i, (score, ref, trans) in enumerate(scores[:100]):
    print(f"RANK: {i}\tSCORE: {score}")
    print(f"\tTRUTH: {ref}\n")
    print(f"\tTRANS: {trans}\n")
    print("\n")

print(sorted(nums, reverse=True)[:500])
