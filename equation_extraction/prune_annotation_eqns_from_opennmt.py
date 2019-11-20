import os
import argparse
import re

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--annotation-list')
    parser.add_argument('--src-train')
    parser.add_argument('--tgt-train')
    parser.add_argument('--src-val')
    parser.add_argument('--tgt-val')
    args = parser.parse_args()
    return args





if __name__ == '__main__':

    pattern = '([0-9]{4}\.[0-9]{5})'
    pattern = re.compile(pattern)

    args = parse_args()
    annotated_papers = set()
    with open(args.annotation_list) as annotated:
        for line in annotated:
            paper = re.findall(pattern, line)[0]
            annotated_papers.add(paper)
    print(len(annotated_papers))

    x = 0
    y = 0

    with open(args.src_train) as src_train, open(args.tgt_train) as tgt_train:
        src_path, src_basefile = os.path.split(args.src_train)
        src_basename, src_ext = os.path.splitext(src_basefile)
        tgt_path, tgt_basefile = os.path.split(args.tgt_train)
        tgt_basename, tgt_ext = os.path.splitext(tgt_basefile)
        src_annotation_excluded_fn = os.path.join(src_path, os.path.join(f'{src_basename}_ann-excluded{src_ext}'))
        tgt_annotation_excluded_fn = os.path.join(tgt_path, os.path.join(f'{tgt_basename}_ann-excluded{tgt_ext}'))

        with open(src_annotation_excluded_fn, 'w') as src_out, open(tgt_annotation_excluded_fn, 'w') as tgt_out:
            for src_line, tgt_line in zip(src_train, tgt_train):
                src_paper = re.findall(pattern, src_line)[0]
                if src_paper in annotated_papers:
                    x += 1
                else:
                    y += 1
                    src_out.write(src_line)
                    tgt_out.write(tgt_line)
    print(x, y)


    x = 0
    y = 0

    with open(args.src_val) as src_val, open(args.tgt_val) as tgt_val:
        src_path, src_basefile = os.path.split(args.src_val)
        src_basename, src_ext = os.path.splitext(src_basefile)
        tgt_path, tgt_basefile = os.path.split(args.tgt_val)
        tgt_basename, tgt_ext = os.path.splitext(tgt_basefile)
        src_annotation_excluded_fn = os.path.join(src_path, os.path.join(f'{src_basename}_ann-excluded{src_ext}'))
        tgt_annotation_excluded_fn = os.path.join(tgt_path, os.path.join(f'{tgt_basename}_ann-excluded{tgt_ext}'))

        with open(src_annotation_excluded_fn, 'w') as src_out, open(tgt_annotation_excluded_fn, 'w') as tgt_out:
            for src_line, tgt_line in zip(src_val, tgt_val):
                src_paper = re.findall(pattern, src_line)[0]
                if src_paper in annotated_papers:
                    x += 1
                else:
                    y += 1
                    src_out.write(src_line)
                    tgt_out.write(tgt_line)
    print(x, y)
