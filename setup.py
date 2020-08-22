""" setuptools-based setup module. """

import os
from setuptools import setup, find_packages
import re
import sys
import platform
from subprocess import check_call, check_output

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion

here = os.path.abspath(os.path.dirname(__file__))

EXTRAS_REQUIRE = {
    "dev": ["jupyter", "jupyter-contrib-nbextensions",],
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
    description="A framework for assembling probabilistic models from text and software.",
    url="https://ml4ai.github.io/automates",
    author="ML4AI",
    author_email="pauldhein@email.arizona.edu",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="assembling models from software",
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "antlr4-python3-runtime==4.8",
        "Flask==1.1.1",
        "flask_codemirror==1.1",
        "flask_wtf==0.14.3",
        "future==0.18.2",
        "matplotlib==3.2.1",
        "networkx==2.4",
        "nltk==3.4.5",
        "notebook==6.0.3",
        "numpy==1.18.2",
        "pandas==1.0.3",
        "plotly==4.5.4",
        "pygraphviz==1.5",
        "pytest==5.4.1",
        "pytest-cov==2.8.1",
        "Pygments==2.3.1",
        "torchtext==0.5.0",
        "SALib==1.3.8",
        "seaborn==0.10.0",
        "scikit_learn==0.22.2.post1",
        "SPARQLWrapper==1.8.5",
        "sympy==1.5.1",
        "torch==1.4.0",
        "tqdm==4.29.0",
        "WTForms==2.2.1",
        "flask-codemirror",
        "scipy",
        "ruamel.yaml",
        "pygments",
    ],
    extras_require=EXTRAS_REQUIRE,
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "delphi = delphi.apps.cli:main",
            "delphi_rest_api = delphi.apps.rest_api.run:main",
            "codex = delphi.apps.CodeExplorer.app:main",
        ]
    },
)
