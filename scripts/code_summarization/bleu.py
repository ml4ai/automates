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
    score = sentence_bleu([reference], translation, weights=(0.25, 0.25, 0.25, 0.25))
    scores.append((score, reference, translation))

nums = [s for s, _, _ in scores]
print(f"Average BLEU score: {np.mean(nums)}")
