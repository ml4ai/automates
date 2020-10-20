import argparse
import glob
import json
import os
import re
from difflib import SequenceMatcher
from pprint import pprint
from collections import defaultdict
from normalize import normalize, render
from latex_tokenizer import *
from align_eq_bb import tokens_to_string

NO_DESC = "<<NO_DESC>>"
NO_LATEX = "<<NO_LATEX>>"

DEBUG = False
syn_pattern = re.compile(r'(\w+)\(.*\)')

stops = ["a", "about", "above", "after", "again", "against", "ain", "all", "am", "an", "and", "any", "are",
         "aren", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
         "but", "by", "can", "couldn", "couldn't", "did", "didn", "didn't", "do", "does", "doesn",
         "doesn't", "doing", "don", "don't", "down", "during", "each", "few", "for", "from", "further",
         "had", "hadn", "hadn't", "has", "hasn", "hasn't", "have", "haven", "haven't", "having", "he", "her",
         "here", "hers", "herself", "him", "himself", "his", "how", "if", "in", "into", "is", "isn", "isn't",
         "it", "it's", "its", "itself", "just", "me", "mightn", "mightn't", "more", "most", "mustn", "mustn't",
         "my", "myself", "needn", "needn't", "no", "nor", "not", "now", "of", "off", "on", "once", "only", "or",
         "other", "our", "ours", "ourselves", "out", "over", "own", "re", "same", "shan't", "she", "she's",
         "should", "should've", "shouldn", "shouldn't", "so", "some", "such", "than", "that", "that'll", "the",
         "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those", "through",
         "to", "too", "under", "until", "up", "very", "was", "wasn", "wasn't", "we", "were", "weren", "weren't",
         "what", "when", "where", "which", "while", "who", "whom", "why", "will", "with", "won", "won't", "wouldn",
         "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
         "could", "he'd", "he'll", "he's", "here's", "how's", "i'd", "i'll", "i'm", "i've", "let's", "ought",
         "she'd", "she'll", "that's", "there's", "they'd", "they'll", "they're", "they've", "we'd", "we'll",
         "we're", "we've", "what's", "when's", "where's", "who's", "why's", "would"]

class Annotation:
    def __init__(self, paper_id, eqn_id, identifiers, descriptions, latex=None):
        self.paper_id = paper_id
        self.eqn_id = eqn_id
        self.identifiers = set(identifiers) #fixme -- set, but make sure the preds idents are not scrambled
        self.identifier_synonyms = self.identifiers.union(set(list(self.identifier_synonyms())))
        self.descriptions = set([self.trim_description(d) for d in descriptions])
        self.latex = set(latex)

    def identifier_synonyms(self):
        for identifier in self.identifiers:
            formula_outer = re.findall(syn_pattern, identifier)
            for outer in formula_outer:
                yield outer

    def __repr__(self):
        return f'Annotation(paper_id={self.paper_id}, eqn_id={self.eqn_id}, identifiers={self.identifiers}, latex={self.latex}, descriptions={self.descriptions})'

    def key(self):
        return (self.paper_id, self.eqn_id)

    def trim_description(self, d):
        d = d.strip()
        if d[0] == '(' and not d[-1] == ')':
            d = d[1:]
        if d[-1] == ')' and '(' not in d:
            d = d[:-1]
        if d[-1] in ['.', ',', ';', ':', '|']:
            d = d[:-1]
        if d[-1] == ')' and not d[0] == '(':
            d = d[:-1]
        d = d.strip()
        d = d.replace("- ", "")
        return d


    # Strict matching
    def matches_pred_strict(self, other, comparison_field, segmentation_only):
        # one of the pred.identifiers matches one of self.identifiers
        matched_identifiers = self.match_identifiers(other, comparison_field)
        if segmentation_only:
            return self.paper_id == other.paper_id and self.eqn_id == other.eqn_id \
               and len(matched_identifiers) > 0
        # one of the pred.descriptions matches one of self.descriptions
        matched_descriptions = self.descriptions.intersection(other.descriptions)
        # pprint(matched_descriptions)
        # and it's the right paper and eqn
        return self.paper_id == other.paper_id and self.eqn_id == other.eqn_id \
               and len(matched_identifiers) > 0 and len(matched_descriptions) > 0

    # Lenient matching
    def matches_pred_lenient(self, other, comparison_field, segmentation_only):
        # one of the pred.identifiers matches one of self.identifiers
        # Here we remain strict bc variables are short and allowing non-exact matches
        # would inflate scores...
        # matched_identifiers = self.match_identifiers(other, comparison_field)
        matched_identifiers = self.match_identifiers_lenient(other, comparison_field)
        if segmentation_only:
            return self.paper_id == other.paper_id and self.eqn_id == other.eqn_id \
               and len(matched_identifiers) > 0
        # one of the pred.descriptions is a substring of one of self.descriptions
        # (bidirectional subsumption)
        matched_descriptions = self.descriptions_that_subsume(other.descriptions) + other.descriptions_that_subsume(self.descriptions)
        # pprint(matched_descriptions)
        return self.paper_id == other.paper_id and self.eqn_id == other.eqn_id \
               and len(matched_identifiers) > 0 and len(matched_descriptions) > 0

    # Lenient matching
    def matches_pred_soft(self, other, comparison_field, segmentation_only):
        # one of the pred.identifiers matches one of self.identifiers
        # Here we remain strict bc variables are short and allowing non-exact matches
        # would inflate scores...
        # matched_identifiers = self.match_identifiers(other, comparison_field)
        matched_identifiers = self.match_identifiers_lenient(other, comparison_field)
        if segmentation_only:
            return self.paper_id == other.paper_id and self.eqn_id == other.eqn_id \
                   and len(matched_identifiers) > 0
        # one of the pred.descriptions is a substring of one of self.descriptions
        # (bidirectional subsumption)
        matched_descriptions = self.descriptions_that_overlap(other.descriptions) + other.descriptions_that_overlap(
            self.descriptions)
        # pprint(matched_descriptions)
        return self.paper_id == other.paper_id and self.eqn_id == other.eqn_id \
               and len(matched_identifiers) > 0 and len(matched_descriptions) > 0

    def match_identifiers(self, other, comparison_field):
        if comparison_field == 'text':
            return self.identifiers.intersection(other.identifiers)
        elif comparison_field == 'latex':
            return self.latex.intersection(other.latex)
        else:
            raise Exception(f"Unsupported comparison_field: {comparison_field}")

    def match_identifiers_lenient(self, other, comparison_field):
        if comparison_field == 'text':
            return self.identifier_synonyms.intersection(other.identifier_synonyms)
        elif comparison_field == 'latex':
            return self.latex.intersection(other.latex)
        else:
            raise Exception(f"Unsupported comparison_field: {comparison_field}")

    def descriptions_that_subsume(self, other_descriptions):
        desc_that_subsume = []
        for d in other_descriptions:
            desc_that_subsume.extend(self.descriptions_with_substring(d))
        return desc_that_subsume

    def descriptions_with_substring(self, s):
        return [d for d in self.descriptions if s in d]

    def descriptions_that_overlap(self, other_descriptions):
        # find common subsequence
        # filter with lucene stop words
        # if any survive, then there is overlap
        desc_that_overlap = []
        for other_d in other_descriptions:
            desc_that_overlap.extend(self.descriptions_with_overlap(other_d))
        return desc_that_overlap

    def descriptions_with_overlap(self, other_d):
        return [d for d in self.descriptions if len(self.longest_subsequence_filtered(d, other_d)) > 0]

    def longest_subsequence_filtered(self, s1, s2):
        def lcs(a, b):
            matcher = SequenceMatcher(None, a, b)
            match = matcher.find_longest_match(0, len(a), 0, len(b))
            return a[match.a:match.a + match.size]
        longest = lcs(s1.split(' '), s2.split(' '))
        longest_no_stops = [w for w in longest if w not in stops]
        return longest_no_stops
        # if len(longest_no_stops) > 0:
        #     return ' '.join(longest)



    def has_match_in_others(self, others, mode, comparison_field, segmentation_only):
        from_same_eqn = [a for a in others if a.key() == self.key()]
        if mode == 'strict':
            return self.has_strict_match_in_others(from_same_eqn, comparison_field, segmentation_only)
        elif mode == 'lenient':
            return self.has_lenient_match_in_others(from_same_eqn, comparison_field, segmentation_only)
        elif mode == 'soft':
            return self.has_soft_match_in_others(from_same_eqn, comparison_field, segmentation_only)
        else:
            raise ValueError(f"Invalid mode: {mode}")

    def has_strict_match_in_others(self, others, comparison_field, segmentation_only):
        for other_ann in others:
            if self.matches_pred_strict(other_ann, comparison_field, segmentation_only):
                return True
        return False

    def has_lenient_match_in_others(self, others, comparison_field, segmentation_only):
        for other_ann in others:
            if self.matches_pred_lenient(other_ann, comparison_field, segmentation_only):
                return True
        return False

    def has_soft_match_in_others(self, others, comparison_field, segmentation_only):
        for other_ann in others:
            if self.matches_pred_soft(other_ann, comparison_field, segmentation_only):
                return True
        return False


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", dest="gold_dir")
    parser.add_argument("-l", dest="latex_dir")
    parser.add_argument("-p", dest="pred_dir")
    args = parser.parse_args()
    return args





def read_annotations(ann_file, latex_file=None):
    basename = os.path.split(os.path.splitext(ann_file)[0])[1]
    paper_id, eqn_id = basename.split("_")

    annotations_latex = list(get_latex(latex_file))
    with open(ann_file) as f:
        annotations = json.load(f)
        for i, a in enumerate(annotations):
            if 'equation' in a:
                eqn_mentions = a['equation']
                identifiers = get_values(eqn_mentions)
                identifiers = [x.replace(' ', '') for x in identifiers]
                # descriptions
                if 'description' not in a:
                    descriptions = [NO_DESC]
                else:
                    desc_mentions = a['description']
                    descriptions = get_values(desc_mentions)
                # latex
                if i < len(annotations_latex):
                    latex = annotations_latex[i]
                else:
                    latex = [NO_LATEX]
                ann = Annotation(paper_id, eqn_id, identifiers, descriptions, latex)
                # print(ann)
                yield ann

def get_latex(filename):
    if not os.path.exists(filename):
        return [NO_LATEX]
    anns = defaultdict(dict)
    with open(filename) as f:
        lines = [x.strip() for x in f.readlines()]
        for line in lines:
            aid, cid, _, p, r, f, latex = line.split("\t")
            aid = int(aid)
            cid = int(cid)
            f = float(f)
            if cid in anns[aid]:
                anns[aid][cid].append((f, latex))
            else:
                anns[aid][cid] = [(f, latex)]
    for aid in anns:
        kept_latex = []
        for cid in anns[aid]:
            max_f = max(anns[aid][cid], key=lambda x: x[0])[0]
            if max_f > 0.0:
                keep = [x[1] for x in anns[aid][cid] if x[0] == max_f]
                keep = [format_latex_for_eval(x) for x in keep]
                # print(keep)
                # print()
                kept_latex.extend(keep)
        if len(kept_latex) == 0:
            kept_latex = [NO_LATEX]
        yield kept_latex

def format_latex_for_eval(latex):
    latex = remove_label(latex)
    try:
        latex = tokens_to_string(normalize(LatexTokenizer(latex)))
    except:
        pass
    return latex.replace(' ', '')

def remove_label(s):
    return re.sub(re.compile('\\\label ?\{.+\} *'), '', s)

# list of mentions, each mention is a dict, in the dict['chars'] is
# a list of glyph bboxes, each bbox has a value -- get these
def get_values(mentions):
    values = []
    for mention in mentions:
        mention_tokens = []
        for token in mention:
            token_string = ""
            for bbox in token['chars']:
                token_string += bbox['value']
            mention_tokens.append(token_string)
        values.append(" ".join(mention_tokens))
    return values

def load_gold(gold_dir, latex_dir):
    gold_files = glob.glob(f'{gold_dir}/*')
    for fn in gold_files:
        basename = os.path.splitext(os.path.split(fn)[1])[0]
        latex_fn = os.path.join(latex_dir, basename, 'aligned.tsv')
        file_annotations = list(read_annotations(fn, latex_fn))
        for a in file_annotations:
            # print(a)
            yield a

def load_predictions(pred_dir):
    pred_files = glob.glob(f'{pred_dir}/*')
    for fn in pred_files:
        with open(fn) as f:
            for line in f:
                # print(line)
                j = json.loads(line)
                desc = j['definitions']
                if len(desc) == 0:
                    desc = [NO_DESC]
                elif len(desc) == 1:
                    desc = desc[0]
                else:
                    raise Exception(f"I expected the len(desc) <= 1 (desc={desc})")
                latex = j['latexIdentifier']
                rendered = latex
                for greek_word in word2greek:
                    rendered = re.sub(re.compile(greek_word), word2greek[greek_word], rendered)
                # rendered = [''.join(list(render(latex))).strip().replace(' ', '')]
                rendered = [''.join(list(render(rendered))).strip().replace(' ', '')]
                latex = latex.replace(' ', '')
                # print("orig:", latex)
                latex = [format_latex_for_eval(latex)]
                # print("normed:", latex)
                # print()
                # rendered = ''.join(list(render(latex)))
                ann = Annotation(j['paperId'], j['eqnId'], rendered, desc, latex)
                # print(ann)
                yield ann

def run_evaluation(mode, comparison_field, segmentation_only):
    args = parse_args()

    gold_annotations = defaultdict(list)
    predictions = defaultdict(list)

    # get the gold files
    flat_gold = list(load_gold(args.gold_dir, args.latex_dir))
    for ann in flat_gold:
        gold_annotations[ann.key()].append(ann)
    # if DEBUG:
    #     print(f"There are {len(flat_gold)} gold annotation identifiers")
        # pprint(flat_gold[:100])
        # relevant = gold_annotations[('1801.01145', 'equation0003')]
        # pprint(relevant)

    # TODO: get the latex alignments for each gold annotation

    # get the prediction files
    flat_preds = list(load_predictions(args.pred_dir))
    for ann in flat_preds:
        predictions[ann.key()].append(ann)
    # if DEBUG:
        # print('\n======================================================\n')
        # print(f"There are {len(flat_preds)} predicted annotation identifiers")
        # relevant = predictions[('1801.01145', 'equation0003')]
        # pprint(relevant)
        # pprint(flat_preds[:100])

    if DEBUG:
        with open('dev_comparison.txt', 'w') as debug_out:
            for key in gold_annotations:
                print("---------------------------------------------------", file=debug_out)
                print("\n", key, file=debug_out)
                print("GOLD:", file=debug_out)
                pprint(gold_annotations[key], stream=debug_out)
                print("\nPRED:", file=debug_out)
                pprint(predictions[key], stream=debug_out)

    gold_eqns = set([x.paper_id for x in flat_gold])
    pred_eqns = set([x.paper_id for x in flat_preds])
    # print(gold_eqns.difference(pred_eqns))
    # print(pred_eqns.difference(gold_eqns))
    # pprint(gold_eqns)
    # pprint(pred_eqns)


    # for each equation:
    # TP = the number of predictions that match
    true_matches = [pred.has_match_in_others(flat_gold, mode, comparison_field, segmentation_only) for pred in flat_preds]
    tp = true_matches.count(True)

    # FP = the number of predictions that don't match
    fp = true_matches.count(False)

    # FN = the number of gold that aren't matched
    found_gold = [ann.has_match_in_others(flat_preds, mode, comparison_field, segmentation_only) for ann in flat_gold]
    fn = found_gold.count(False)

    # Scores
    print(f'tp:{tp}, fp:{fp}, fn:{fn}')
    if (tp + fp) == 0:
        precision = 0
    else:
        precision = tp / (tp + fp)
    if (tp + fn) == 0:
        recall = 0
    else:
        recall = tp / (tp + fn)
    if (precision + recall) == 0:
        f1 = 0
    else:
        f1 = 2 * (precision * recall) / (precision + recall)
    return (precision, recall, f1)

# todo: add the segmentation alone eval


greek2word = {'α':'alpha', 'β':'beta', 'γ':'gamma', 'δ':'delta', 'ε':'epsilon', 'ζ':'zeta', 'η':'eta',
              'θ':'theta','ι':'iota', 'κ':'kappa','λ':'lambda', 'μ':'mu', 'ν':'nu', 'ξ':'xi', 'ο':'omikron',
              'π':'pi', 'ρ':'rho', 'σ':'sigma', 'τ':'tau', 'υ':'upsilon', 'φ':'phi', 'χ':'chi',
              'ψ':'psi', 'ω':'omega'}
word2greek = {'\\\\alpha': 'α', '\\\\beta': 'β',    '\\\\gamma': 'γ',   '\\\\delta': 'δ',   '\\\\epsilon': 'ε', '\\\\zeta': 'ζ',
              '\\\\eta': 'η',   '\\\\theta': 'θ',   '\\\\iota': 'ι',    '\\\\kappa': 'κ',   '\\\\lambda': 'λ',  '\\\\mu': 'μ',
              '\\\\nu': 'ν',    '\\\\xi': 'ξ',      '\\\\omikron': 'ο', '\\\\pi': 'π',      '\\\\rho': 'ρ',     '\\\\sigma': 'σ',
              '\\\\tau': 'τ',   '\\\\upsilon': 'υ', '\\\\phi': 'φ',     '\\\\chi': 'χ',     '\\\\psi': 'ψ',     '\\\\omega': 'ω',
              '\\\\Alpha': 'Α', '\\\\Beta': 'Β',    '\\\\Gamma': 'Γ',   '\\\\Delta': 'Δ',   '\\\\Epsilon': 'Ε', '\\\\Zeta': 'Ζ',
              '\\\\Eta': 'Η',   '\\\\Theta': 'Θ',   '\\\\Iota': 'Ι',    '\\\\Kappa': 'Κ',   '\\\\Lambda': 'Λ',  '\\\\Mu': 'Μ',
              '\\\\Nu': 'Ν',    '\\\\Xi': 'Ξ',      '\\\\Omicron': 'Ο', '\\\\Pi': 'Π',      '\\\\Rho': 'Ρ',     '\\\\Sigma': 'Σ',
              '\\\\Tau': 'Τ',   '\\\\Upsilon': 'Υ', '\\\\Phi': 'Φ',     '\\\\Chi': 'Χ',     '\\\\Psi': 'Ψ',     '\\\\Omega': 'Ω'}



if __name__ == "__main__":
    print("\n------------------ FULL EVAL ------------------\n")
    print("Identifier Unicode Value Comparison")
    p_strict, r_strict, f1_strict = run_evaluation("strict", "text", segmentation_only=False)
    # sys.exit()
    print(f"STRICT\tP={p_strict}\tR:{r_strict}\tF1:{f1_strict}")
    p_lenient, r_lenient, f1_lenient = run_evaluation("lenient", "text", segmentation_only=False)
    print(f"LENIENT\tP={p_lenient}\tR:{r_lenient}\tF1:{f1_lenient}")
    p_soft, r_soft, f1_soft = run_evaluation("soft", "text", segmentation_only=False)
    print(f"SOFT\tP={p_soft}\tR:{r_soft}\tF1:{f1_soft}")

    print("\nIdentifier Latex Comparison")
    p_strict, r_strict, f1_strict = run_evaluation("strict", "latex", segmentation_only=False)
    print(f"STRICT\tP={p_strict}\tR:{r_strict}\tF1:{f1_strict}")
    p_lenient, r_lenient, f1_lenient = run_evaluation("lenient", "latex", segmentation_only=False)
    print(f"LENIENT\tP={p_lenient}\tR:{r_lenient}\tF1:{f1_lenient}")

    print("\n-------------- SEGMENTATION ONLY EVAL --------------\n")
    print("Identifier Unicode Value Comparison")
    p_strict, r_strict, f1_strict = run_evaluation("strict", "text", segmentation_only=True)
    print(f"STRICT\tP={p_strict}\tR:{r_strict}\tF1:{f1_strict}")
    p_lenient, r_lenient, f1_lenient = run_evaluation("lenient", "text", segmentation_only=True)
    print(f"LENIENT\tP={p_lenient}\tR:{r_lenient}\tF1:{f1_lenient}")

    print("\nIdentifier Latex Comparison")
    p_strict, r_strict, f1_strict = run_evaluation("strict", "latex", segmentation_only=True)
    print(f"STRICT\tP={p_strict}\tR:{r_strict}\tF1:{f1_strict}")
    p_lenient, r_lenient, f1_lenient = run_evaluation("lenient", "latex", segmentation_only=True)
    print(f"LENIENT\tP={p_lenient}\tR:{r_lenient}\tF1:{f1_lenient}")
