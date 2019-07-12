import argparse
import os

# header = """ 
# \documentclass[12pt]{article}
# \pagestyle{empty}
# \\usepackage{amsmath}
# \\begin{document}
# """

footer = """
\end{document}
"""

header = """
\documentclass{standalone}
\\begin{document}
"""

begin_eqn = """ $\displaystyle """
end_eqn = """ $ """
# begin_eqn = """ \\begin{displaymath}"""
# end_eqn = """ \\end{displaymath}"""

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', help='split or combine')
    parser.add_argument('--outdir', help='directory to put the split apart eqn tex files into')
    parser.add_argument('--eqn-file', help='tex file with all equations to be split apart')
    parser.add_argument('--infile', help='results.txt file from the im2markup inference')
    parser.add_argument('--combined-file', help='final tex file with all eqns')
    args = parser.parse_args()
    return args


def mk_individual_eqn_files(eqn_file, outdir):
    with open(eqn_file) as eqn_file:
        lines = eqn_file.readlines()
        num_lines = len(lines)
        counter = 0
        for i in range(0,num_lines, 4):
            begin = lines[i]
            eqn = lines[i + 1]
            end = lines[i + 2]

            eqn_str = "equation{:04}.tex".format(counter)
            fn = os.path.join(outdir, eqn_str)

            with open(fn, 'w') as outfile:
                outfile.write(header + "\n")
                outfile.write(begin_eqn + "\n")
                outfile.write(eqn)
                outfile.write(end_eqn + "\n")
                outfile.write(footer + "\n")

            counter += 1

def mk_combined_file_from_results(infile, combined_file):
    with open(combined_file, 'w') as outfile:
        outfile.write(header + "\n")
        with open(infile) as results_file:
            lines = results_file.readlines()
            results = []
            for line in lines:
                fields = line.split("\t")
                filename = fields[0]
                # print(filename)
                idx = int(filename[3:-4]) #fixme
                eqn = fields[2]
                results.append((idx, eqn))
            results.sort()
            for item in results:
                outfile.write(f"\n equation {item[0]}\n")
                outfile.write(begin_eqn + "\n")
                outfile.write(item[1] + "\n")
                outfile.write(end_eqn + "\n")
        outfile.write(footer + "\n")

def main(args):
    if args.mode == "split":
        mk_individual_eqn_files(args.eqn_file, args.outdir)
    elif args.mode == "combine":
        mk_combined_file_from_results(args.infile, args.combined_file)
    else:
        print("nice try goober. invalid mode:", args.mode)


if __name__ == '__main__':
    args = parse_args()
    main(args)
