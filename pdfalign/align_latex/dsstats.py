import os
import re
import sys
import json
import glob

annotation_dir = sys.argv[1]

paper_id_rx = re.compile(r'\d+\.\d+')

paper_ids = []
n_equations = 0
n_anns = []
n_comps = []
n_desc = []
desc_len = []

for filename in glob.glob(os.path.join(annotation_dir, '*.json')):
    with open(filename) as f:
        data = json.load(f)
    n_equations += 1
    paper_ids.append(paper_id_rx.search(filename).group())
    n_anns.append(len(data))
    for ann in data:
        if 'equation' in ann:
            n_comps.append(len(ann['equation']))
            n_desc.append(len(ann.get('description', [])))
            for desc in ann.get('description', []):
                desc_len.append(len(desc))

print(len(set(paper_ids)), 'total papers')
print(n_equations, 'total equations')
print(sum(n_anns), 'total annotations')
print(n_desc.count(0), 'total annotations without description')
print(f'{min(n_anns)}/{max(n_anns)}/{sum(n_anns)/len(n_anns)} annotations')
print(f'{min(n_comps)}/{max(n_comps)}/{sum(n_comps)/len(n_comps)} components')
print(f'{min(desc_len)}/{max(desc_len)}/{sum(desc_len)/len(desc_len)} description length')

