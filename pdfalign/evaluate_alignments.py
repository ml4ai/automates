import argparse
import glob
import json
import os
from collections import defaultdict

class Annotation:
    def __init__(self, paper_id, eqn_id, identifiers, descriptions, latex=None):
        self.paper_id = paper_id
        self.eqn_id = eqn_id
        self.identifiers = identifiers
        self.descriptions = descriptions
        self.latex = latex
        # fixme -- match on latex

    def key(self):
        return (self.paper_id, self.eqn_id)

    # Strict matching
    def matches_pred_strict(self, pred):
        # one of the pred.identifiers matches one of self.identifiers
        matched_identifiers = self.identifiers.intersection(pred.identifiers)
        # one of the pred.descriptions matches one of self.descriptions
        matched_descriptions = self.descriptions.intersection(pred.descriptions)
        # and it's the right paper and eqn
        return self.paper_id == pred.paper_id and self.eqn_id == pred.eqn_id \
               and len(matched_identifiers) > 0 and len(matched_descriptions) > 0

    # Lenient matching
    def matches_pred_lenient(self, pred):
        # one of the pred.identifiers matches one of self.identifiers
        # Here we remain strict bc variables are short and allowing non-exact matches
        # would inflate scores...
        matched_identifiers = self.identifiers.intersection(pred.identifiers)
        # one of the pred.descriptions is a substring of one of self.descriptions
        # fixme -- bidirectional subsumption
        matched_descriptions = self.descriptions_that_subsume(pred.descriptions)
        return self.paper_id == pred.paper_id and self.eqn_id == pred.eqn_id \
               and len(matched_identifiers) > 0 and len(matched_descriptions) > 0

    def descriptions_that_subsume(self, other_descriptions):
        desc_that_subsume = []
        for d in other_descriptions:
            desc_that_subsume.extend(self.descriptions_with_substring(d))
        return desc_that_subsume

    def descriptions_with_substring(self, s):
        return [d for d in self.descriptions if s in d]

    def has_match_in_others(self, others, mode):
        from_same_eqn = [a for a in others if a.key() == self.key()]
        if mode == 'strict':
            return self.has_strict_match_in_others(from_same_eqn)
        elif mode == 'lenient':
            return self.has_lenient_match_in_others(from_same_eqn)
        else:
            raise ValueError(f"Invalid mode: {mode}")

    def has_strict_match_in_others(self, others):
        for other_ann in others:
            if self.matches_pred_strict(other_ann):
                return True
        return False

    def has_lenient_match_in_others(self, others):
        for other_ann in others:
            if self.matches_pred_lenient(other_ann):
                return True
        return False



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", dest="gold_dir")
    parser.add_argument("-p", dest="pred_dir")
    args = parser.parse_args()
    return args


# list of mentions, each mention is a dict, in the dict['chars'] is
# a list of glyph bboxes, each bbox has a value -- get these
def get_values(mentions):
    for mention in mentions:
        for bbox in mention['chars']:
            yield bbox['value']



def read_annotations(ann_file):
    basename = os.path.split(os.path.splitext(ann_file)[0])[1]
    paper_id, eqn_id = basename.split("_")

    with open(ann_file) as f:
        annotations = json.load(f)
        for a in annotations:
            eqn_mentions = a['equation']
            identifiers = list(get_values(eqn_mentions))
            desc_mentions = a['definition']
            descriptions = list(get_values(desc_mentions))
            # todo: load the latex too
            yield Annotation(paper_id, eqn_id, identifiers, descriptions)

def load_gold(gold_dir):
    gold_files = glob.glob(f'{gold_dir}/*')
    for fn in gold_files:
        file_annotations = list(read_annotations(fn))
        for a in file_annotations:
            yield a

def load_predictions(pred_dir):
    pred_files = glob.glob(f'{pred_dir}/*')
    for fn in pred_files:
        with open(fn) as f:
            for line in f:
                j = json.loads(line)
                yield Annotation(j['paperId'], j['eqnId'], j['latexIdentifier'], j['definitions'])

def run_evaluation(mode):
    args = parse_args()

    gold_annotations = defaultdict(list)
    predictions = defaultdict(list)

    # get the gold files
    flat_gold = list(load_gold(args.gold_dir))
    for ann in flat_gold:
        gold_annotations[ann.key()].append(ann)

    # get the prediction files
    flat_preds = list(load_predictions(args.pred_dir))
    for ann in flat_preds:
        predictions[ann.key()].append(ann)

    # for each equation:
    # TP = the number of predictions that match
    true_matches = [pred.has_match_in_others(flat_gold, mode) for pred in flat_preds]
    tp = true_matches.count(True)

    # FP = the number of predictions that don't match
    fp = true_matches.count(False)

    # FN = the number of gold that aren't matched
    found_gold = [ann.has_match_in_others(flat_preds, mode) for ann in flat_gold]
    fn = found_gold.count(False)

    # Scores
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * (precision * recall) / (precision + recall)
    return (precision, recall, f1)

# todo: add the segmentation alone eval
# todo: make sure logic works for None Description.... special token for No Description


if __name__ == "__main__":
    p_strict, r_strict, f1_strict = run_evaluation("strict")
    p_lenient, r_lenient, f1_lenient = run_evaluation("lenient")
