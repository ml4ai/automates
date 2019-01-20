import os, glob
import tarfile
import argparse
import subprocess

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dirname') # the path with the arxiv arXiv_src_*_*.tar files
    parser.add_argument('outputdir')  # the path with the arxiv arXiv_src_*_*.tar files
    parser.add_argument('--keepall', action='store_true', default=False)
    args = parser.parse_args()
    return args

def is_pdf(f):
    return f.endswith(".pdf")

def is_gz(f):
    return f.endswith(".gz")

# gunzip file, return name of uncompressed file
def gunzip_file(f):
    try:
        # gunzip(f)
        subprocess.check_call(['gunzip', f])
    except:
        print "WARNING: Didn't unzip, check to make sure the file ({0}) wasn't already uncompressed".format(f)
    return f[:-3]  # the name after gunzip

# make a directory for the paper file(s), return path
def mk_paper_dir(f):
    paper_dir = f + "_dir"
    if not os.path.exists(paper_dir):
        os.makedirs(paper_dir)
    return paper_dir

# wdir: the path with the arxiv arXiv_src_*_*.tar files
def expand_arxiv(wdir, outdir, keep_all):
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    arxiv_files = glob.glob(os.path.join(wdir, "*.tar"))
    print "arXiv dump files to be expanded:", arxiv_files

    # expand the initial files, e.g., arXiv_src_1808_023.tar
    for fn in arxiv_files:
        print "Extracting files from", fn
        assert(tarfile.is_tarfile(fn) == True) # for good measure...
        tar = tarfile.open(fn)
        extracted_files = tar.getnames()
        tar.extractall(path=outdir)
        tar.close()

        counter = 0
        for f in extracted_files:
            # path to the extracted file that needs to be handled
            f = os.path.join(outdir, f)

            # We expect that this file will be a gzipped file or a pdf
            # If it's a gzipped file (i.e., with latex source):
            if is_gz(f):
                counter += 1
                # gunzip it, return newly uncompressed filename
                base_path = gunzip_file(f)
                # make dir where paper contents will go
                paper_dir = mk_paper_dir(base_path)

                # Either the uncompressed file will be a tar file or a single tex file (w/o the tex extension!)
                # Case 1: if it's a tar file
                if tarfile.is_tarfile(base_path):
                    # untar it to the paper directory
                    paper_tar = tarfile.open(base_path)
                    paper_tar.extractall(path=paper_dir)
                    paper_tar.close()
                    # Remove the tar file
                    if not keep_all:
                        subprocess.check_call(['rm', base_path])

                # Case 2: it's the tex file missing its extension
                else:
                    # rename it and move to the paper dir
                    base_name = os.path.split(base_path)[1]
                    tex_path = os.path.join(paper_dir, base_name + ".tex")
                    os.rename(base_path, tex_path)

            # Otherwise, if it's a pdf, disregard
            elif is_pdf(f):
                if not keep_all:
                    subprocess.check_call(['rm', f])
            # There are a few other formats, we also will disregard them, but just in case we want to see
            # how many and of what type...
            else:
                print "INFO: didn't handle file ", f
                # not removing here bc we get the main dir in the list, I guess bc of the api for
                # tarfile.getnames()...

        print "... finished extracting {0} papers".format(counter)

if __name__ == '__main__':
    args = parse_args()
    expand_arxiv(args.dirname, args.outputdir, args.keepall)
