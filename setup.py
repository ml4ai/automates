""" setuptools-based setup module. """

import os
from setuptools import setup, find_packages, Extension
import re
import sys
import platform
from subprocess import check_call, check_output
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion

here = os.path.abspath(os.path.dirname(__file__))

EXTRAS_REQUIRE = {
    "dev": [
        "jupyter",
        "jupyter-contrib-nbextensions",
    ],
    "test": ["pytest>=4.4.0", "pytest-cov", "pytest-xdist"],
    "docs": [
        "sphinx",
        "sphinx-rtd-theme",
        "sphinxcontrib-bibtex",
        "sphinxcontrib-trio",
        "recommonmark",
    ],
}

EXTRAS_REQUIRE["all"] = list(
    {dep for deps in EXTRAS_REQUIRE.values() for dep in deps}
)

setup(
    name="automates",
    version="0.1.0",
    description="A framework for assembling scientific models from text, equations, and software.",
    url="https://ml4ai.github.io/automates",
    author="ML4AI",
    author_email="claytonm@email.arizona.edu",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="assembling models from software",
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "antlr4-python3-runtime",
        "dill",
        "Flask",
        "flask_codemirror",
        "flask_wtf",
        "future",
        "matplotlib",
        "networkx",
        "nltk",
        "notebook",
        "numpy",
        "pandas",
        "plotly",
        "pygraphviz",
        "pytest",
        "pytest-cov",
        "python-igraph",
        "Pygments",
        "SALib",
        "seaborn",
        "scikit_learn",
        "SPARQLWrapper",
        "sympy",
        "tqdm",
        "WTForms",
        "flask-codemirror",
        "scipy",
        "ruamel.yaml",
        "pdfminer.six",
        "pdf2image",
        "webcolors",
        "lxml",
        "Pillow",
        "ftfy",
        "fastparquet"
    ],
    extras_require=EXTRAS_REQUIRE,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "codex = automates.apps.CodeExplorer.app:main",
        ]
    },
)
