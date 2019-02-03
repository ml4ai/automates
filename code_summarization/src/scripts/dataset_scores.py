import pickle
import sys

import utils.utils as utils

clfs_path = utils.CODE_CORPUS / "results" / sys.argv[1]
classifications = pickle.load(open(clfs_path, "rb"))
scores = utils.score_classifier(classifications)
print("(P, R, F1) = ({}, {}, {})".format(*scores))
