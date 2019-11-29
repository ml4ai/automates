import os
from glob import glob
from latex_tokenizer import LatexTokenizer, CategoryCode



def find_main_tex_file(dirname):
    r"""looks in a directory for a .tex file that contain the \documentclass directive"""
    # (from https://arxiv.org/help/faq/mistakes#wrongtex)
    #
    # Why does arXiv's system fail to recognize the main tex file?
    #
    # It is possible in writing your latex code to include your \documentclass directive
    # in a file other than the main .tex file. While this is perfectly reasonable for a human
    # who's compling to know which of the tex files is the main one (even when using something
    # obvious as the filename, such as ms.tex), our AutoTeX system will attempt to process
    # whichever file has the \documentclass directive as the main tex file.
    #
    # Note that the system does not process using Makefile or any other manifest-type files.
    for filename in glob(os.path.join(dirname, '*.tex')):
        with open(filename) as f:
            for token in LatexTokenizer(f.read()):
                if token.value == '\\documentclass':
                    return filename
