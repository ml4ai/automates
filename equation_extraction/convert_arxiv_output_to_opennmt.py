import os
import glob
import sys
from collect_data import run_command


def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def get_tex(fn):
    with open(fn) as fi:

        
def gather_opennmt_data(parent_dir, outdir):
    month_dirs = os.listdir(parent_dir)

    counter = 0
    img_names = []
    for month in month_dirs:
        # make output dir for month
        month_out = os.path.join(outdir, month)
        mkdir(month_out)
        # keep an absolute path        
        month_path = os.path.join(parent_dir, month)
        paper_dirs = os.listdir(month_path)
        for paper in paper_dirs:
            # keep an absolute path
            paper_path = os.path.join(month_path, paper)
            equation_dirs = glob.glob(os.path.join(paper_path, "equation*"))
            for eqndir in equation_dirs:
                # keep an absolute path
                eqn_path = os.path.join(paper_path, eqndir)
                eqn_tex_file = os.path.join(eqn_path, "equation.tex")
                eqn_pdf_file = os.path.join(eqn_path, "equation.pdf")
                # if these files exist:
                if os.path.exists(eqn_tex_file) and os.path.exists(eqn_pdf_file):
                    tex = 
                    # make filename with provenance
                    basename = f'{paper}_{eqndir}'
                    run_command(['cp', eqn_pdf_file, os.path.join(month_out, basename + ".pdf")], outdir, 'formatting_for_opennmt_stdout.log')
                    img_names.append(

if __name__ == '__main__':
    args = sys.argv
    parent_dir = args[1]
    outdir = args[2]
    gather_opennmt_data(parent_dir, outdir)
 
