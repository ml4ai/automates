import argparse
import os
from utils import run_command

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--indir', default='.', help='directory with the src and tgt train, val, and test files')
    parser.add_argument('--logfile', default='normalize_formulas.log')
    parser.add_argument('--im2markupdir', default='im2markup', help='path to the im2markup repo, assumes our edits to the repo')
    args = parser.parse_args()
    return args

def mk_file_paths(indir):
    srcs = []
    tgts = []
    for fold in ['train', 'val', 'test']:
        srcs.append(os.path.join(indir, 'src_{0}.txt'.format(fold)))
        tgts.append(os.path.join(indir, 'tgt_{0}.txt'.format(fold)))
    return srcs, tgts

def repair_label_spacing(files, logfile):
    for f in files:
        cmd = ['sed', '-i', "'s/\\label /\\label/g'", f]
        run_command(cmd, '.', logfile)

def norm_files(files, im2latex_dir, logfile):
    pruned_files = []
    for f in files:
        outdir = os.path.dirname(f)
        # remove extension, assumes a `.***` extension
        basename = os.path.basename(f)[:-4]
        outfile = os.path.join(outdir, basename + '-norm.txt')
        pruned_files.append(outfile)
        cmd = ['python', 'scripts/preprocessing/preprocess_formulas.py', '--mode',
               'normalize', '--input-file', f, '--output-file', outfile]
        run_command(cmd, im2latex_dir, logfile)
    return pruned_files

def prune_failed_formulas(src_files, normed_tgt_files, logfile):
    assert len(src_files) == len(normed_tgt_files)
    for i in range(len(src_files)):
        src_file = src_files[i]
        tgt_file = tgt_files[i]
        # assumes a `.***` extension
        src_out_name = src_file[:-4] + "-pruned.txt"
        tgt_out_name = tgt_file[:-4] + "-pruned.txt"
        with open(src_file, 'r') as src, open(tgt_file, 'r') as tgt, open(logfile, 'a') as log:
            with open(src_out_name, 'w') as src_out, open(tgt_out_name, 'w') as tgt_out:
                src_line = src.readline()
                tgt_line = tgt.readline()
                while src_line and tgt_line:
                    if not tgt_line.strip() == 'XXXXXXXXXX':
                        src_out.write(src_line)
                        tgt_out.write(tgt_line)
                    else:
                        log.write("EQN failed and removed:\t", src_line.strip(), "\t", tgt_line)


if __name__ == '__main__':
    args = parse_args()
    # 1) get the files, in order (train, val, test) for src and tgt
    src_files, tgt_files = mk_file_paths(args.indir)

    # 2) replace the `\label ` with `\label` for the normalization
    repair_label_spacing(tgt_files, args.logfile)

    # 3) call the im2markup normalization script
    normed_tgt_files = norm_files(tgt_files, args.im2markupdir, args.logfile)

    # 4) prune images/equations that katex (in the normalization script) couldn't handle
    prune_failed_formulas(src_files, normed_tgt_files)