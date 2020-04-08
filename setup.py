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
    "dev": [
        "jupyter",
        "jupyter-contrib-nbextensions",
    ],
    "test": ["pytest>=4.4.0", "pytest-cov", "pytest-sugar", "pytest-xdist"],
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
    version="0.0.1",
    description="A framework for assembling probabilistic models from text and software.",
    url="https://ml4ai.github.io/automates",
    author="ML4AI",
    author_email="adarsh@email.arizona.edu",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="assembling models from software",
    package_dir = {"":"src"},
    packages=find_packages("src"),
    zip_safe=False,
    install_requires=[
        "plotly",
        "sympy",
        "flask",
        "flask-WTF",
        "flask-codemirror",
        "salib",
        "torch",

        "tqdm",
        "numpy",
        "scipy",
        "matplotlib",
        "seaborn>=0.10.0",
        "pandas",
        "future==0.16.0",
        "networkx",
        "pygraphviz",
        "dataclasses",
        "flask",
        "ruamel.yaml",
        "pygments",
        "flask",
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
