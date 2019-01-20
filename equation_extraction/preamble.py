from __future__ import division
import sys, os, glob, re
from latex import find_main_tex_file
from collections import defaultdict
import operator
import argparse

package_pattern = re.compile("usepackage\[?.*?\]?\{(.+?)\}") # non-greedy
package_pattern_plus = re.compile("usepackage(\[.+?\]\{.+?\})") # non-greedy
square_pattern = re.compile("\[(.+)\]")
curly_pattern = re.compile("\{(.+)\}")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dirname') # the path with the arxiv arXiv_src_*_*.tar files
    parser.add_argument('outputfile')  # the path with the arxiv arXiv_src_*_*.tar files
    parser.add_argument('--finegrained', action='store_true', default=False)
    args = parser.parse_args()
    return args

def get_packages(filename, finegrained):
    packages = []
    # print filename
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line.startswith(r'\usepackage'):
                if finegrained:

                    matches = re.findall(package_pattern_plus, line)
                    if len(matches) > 0:
                        for match in matches:
                            sq_contents = re.findall(square_pattern, match)[0].split(",")
                            curly_contents = re.findall(curly_pattern, match)[0].split(",")
                            for sq in sq_contents:
                                for cu in curly_contents:
                                    packages.append('['+sq.strip()+']'+'{'+cu+'}')
                    else: # backoff
                        matches = re.findall(package_pattern, line)
                        for match in matches:
                            [packages.append(p.strip()) for p in match.split(",")]
                else:
                    matches = re.findall(package_pattern, line)
                    for match in matches:
                        [packages.append(p.strip()) for p in match.split(",")]

                # packages.extend(matches)
    # print packages
    return packages


def find_preamble_packages(inputdir, outfile, finegrained):
    collection_dir = inputdir
    subdirectories = next(os.walk(collection_dir))[1]
    package_counter = defaultdict(int)
    num_mains = 0
    for subdir in subdirectories:
        main_file = find_main_tex_file(os.path.join(collection_dir, subdir))
        # print "Main file for subdir {0}: {1}".format(subdir, main_file)
        if main_file:
            num_mains += 1
            packages = get_packages(main_file, finegrained)
            # if packages:
            for p in packages:
                package_counter[p] += 1
    sorted_packages = sorted(package_counter.iteritems(), key=operator.itemgetter(1), reverse=True)
    with open(outfile, 'w') as outfile:
        outfile.write("From {0} main files:\n".format(num_mains))
        outfile.write("package\tcount\tproportion\n")
        for p in sorted_packages:
            if p[1] > 1:
                pkg, ct = p
                proportion = round(ct/num_mains, 4)
                outfile.write("{0}\t{1}\t{2}\n".format(pkg, ct, proportion))
        # print sorted_packages

if __name__ == '__main__':
    args = parse_args()
    find_preamble_packages(args.dirname, args.outputfile, args.finegrained)
