import os
import argparse
import re
from utils import run_command

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--annotation-list')
    parser.add_argument('--srcdir')
    parser.add_argument('--outdir')

    args = parser.parse_args()
    return args

def mk_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)




if __name__ == '__main__':

    pattern = '([0-9]{4}\.[0-9]{5})'
    pattern = re.compile(pattern)

    args = parse_args()
    annotated_papers = set()
    with open(args.annotation_list) as annotated:
        for eqn in annotated:
            # ex: 1801.00026_equation0000
            eqn = eqn.strip()
            # 1801.00026
            paper = re.findall(pattern, eqn)[0]
            # 1801
            year = paper[0:4]
            # srcdir/1801/1801.00026
            src_paper_dir = os.path.join(os.path.join(args.srcdir, year), paper)
            # outdir/1801.00026_equation0000
            local_paper_dir = os.path.join(args.outdir, paper)
            mk_dir(local_paper_dir)
            # copy files down
            cmd = f'rsync -rtv {src_paper_dir}/* {local_paper_dir}/.'.split(" ")
            print(f"copying files for {eqn}...")
            run_command(cmd, ".", "./copy_src.log")
            print(f" * finished")
