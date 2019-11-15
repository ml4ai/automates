import os
import glob
from collections import defaultdict

def read_scores(fn):
    with open(fn) as f:
        for line in f:
            [ann, comp, color, p, r, f1] = line.split("\t")
            ann = int(ann)
            comp = int(comp)
            p = float(p)
            r = float(r)
            f1 = float(f1)
            yield ann, comp, color, p, r, f1

def main(args):
    frags = os.listdir(args.dirname)
    component_scores = defaultdict(list)
    for frag in frags:
        frag_dir = os.path.join(args.dirname, frag) 
        score_file = os.path.join(frag_dir, 'scores.tsv')
        frag_file = os.path.join(frag_dir, 'fragment.txt')
        with open(frag_file) as f:
            fragment = f.read()
        for scored_component in read_scores(score_file):
            key = scored_component[:2]
            value = (*scored_component, fragment)
            component_scores[key].append(value)
    # sort
    for k in component_scores:
        sorted_by_f1 = list(sorted(component_scores[k], key=lambda x: x[5], reverse=True))
        component_scores[k] = sorted_by_f1[:args.n]

    with open(args.output, 'w') as f:
        for k in sorted(component_scores):
            for row in component_scores[k]:
                row = [str(elem) for elem in row]
                row = '\t'.join(row)
                print(row, file=f)



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dirname')
    parser.add_argument('output')
    parser.add_argument('-n', type=int, default=5)
    args = parser.parse_args()
    main(args)


# <ann_id> <comp_id> <fragment> <f1>
