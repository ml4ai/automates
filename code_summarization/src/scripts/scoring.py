import pickle

from utils.utils import score_classifier

dev_data = pickle.load(open("../../data/results/scores_test.pkl", "rb"))
score_classifier(dev_data)
