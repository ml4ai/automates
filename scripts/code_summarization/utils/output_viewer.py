import random
import nltk

dev_comms = list()
with open("dev.nl", "r") as infile:
    for line in infile.readlines():
        cells = line.strip().split(" ")
        comment = cells[1:-1]
        dev_comms.append(" ".join(comment))

embed_comms = list()
with open("embed_dev.nl", "r") as infile:
    for line in infile.readlines():
        cells = line.strip().split(" ")
        comment = cells
        embed_comms.append(" ".join(comment))

non_embed_comms = list()
with open("non_embed_dev.nl", "r") as infile:
    for line in infile.readlines():
        cells = line.strip().split(" ")
        comment = cells
        non_embed_comms.append(" ".join(comment))


comments = list(zip(dev_comms, embed_comms, non_embed_comms))
# random.shuffle(comments)

comments_with_scores = list()
for dev, emb, non_emb in comments:
    reference = dev.split(" ")
    translation = emb.split(" ")
    emb_score = nltk.translate.bleu_score.sentence_bleu([reference], translation, weights = (0.5, 0.5))

    translation = non_emb.split(" ")
    non_emb_score = nltk.translate.bleu_score.sentence_bleu([reference], translation, weights = (0.5, 0.5))
    comments_with_scores.append((dev, emb, non_emb, emb_score, non_emb_score))

comments_with_scores.sort(key=lambda tup: (tup[3], tup[4]), reverse=True)

for (dev, emb, non_emb, emb_score, non_emb_score) in comments_with_scores[:10]:
    print("GOLD")
    print("{}\n\n".format(dev))

    print("Non Pretrained Embedding")
    print("{}\n\n".format(non_emb))

    print("Pretrained Embedding")
    print("{}\n\n".format(emb))
