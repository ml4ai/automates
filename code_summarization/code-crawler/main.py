from utils.code_crawler import CodeCrawler

# Repo's to use as corpus data

# Scientific packages
import sklearn, skimage, numpy, scipy, sympy
import networkx

# Deep-learning / auto-diff packages
import tensorflow, keras, theano, torch, dynet, autograd, tangent, chainer, mxnet

# I/O and viz packages
import pygame, seaborn, matplotlib, graphviz, pygraphviz, h5py

# Data management packages
import dask, pandas, sqlalchemy


# WORKING: sklearn, numpy, scipy, sympy, mpl, pygame, sqlalchemy, skimage, h5py,
# dask, seaborn, tensorflow, keras, dynet, autograd, tangent, chainer, networkx,
# pandas, theano, torch, mxnet, graphviz, pygraphviz

# NOT WORKING: N/A

# NO FUNCTIONS FOUND: feather

def main():
    modules = [sklearn, numpy, scipy, sympy, matplotlib, pygame, sqlalchemy, skimage, h5py,
               dask, seaborn, tensorflow, keras, dynet, autograd, tangent, chainer,
               networkx, pandas, theano, torch, mxnet, graphviz, pygraphviz]

    output_path = "../data/"
    ccrawler = CodeCrawler(modules=modules)
    print("Building function dict")
    ccrawler.build_function_dict(output_path)
    print("Building code/comment dict")
    ccrawler.build_code_comment_pairs(output_path)
    print("Getting output sentences")
    ccrawler.get_sentence_output(output_path)
    print("Making train/dev/test splits")
    ccrawler.split_code_comment_data(output_path)
    print("done.")


if __name__ == '__main__':
    main()
