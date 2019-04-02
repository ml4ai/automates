#!/usr/bin/env python3
""" This script builds the ASKE deliverable reports as PDFs by combining the
markdown files, using pandoc.

Usage:
    ./build_report.py <report_name>
"""

import os, sys
from glob import glob
import subprocess as sp


def transform_line(line):
    # Transform headers - numbered headings are not supported in Jekyll,
    # and we want them for the LaTeX output.

    if line.startswith("#"):
        header_level = line.split()[0]
        line = line.replace(header_level, header_level[:-1])
        if line.split()[1][0].isdigit():
            line = "# " + " ".join(line.split()[2:])

    # Skip captions intended for web
    if line.startswith("**Figure"):
        line=""

    # Transform math expression delimiters
    line = line.replace("$$", "$")

    # Recursively include markdown files
    if "include_relative" in line:
        filename = line.split()[2]
        with open(filename, "r") as f:
            line = "\n" + "".join([transform_line(line) for line in f])
    return line


def build_report(report_name):
    """ Apply appropriate transformations to markdown files
    so that they can be compiled properly into a PDF report via
    LaTeX. """

    with open("index.md", "r") as f:
        lines = [transform_line(line) for line in f]
    with open("index_transformed.md", "w") as f:
        f.writelines(lines)
    sp.call(
        [
            "pandoc",
            "--template",
            "../pandoc_report_template.tex",
            "--pdf-engine",
            "lualatex",
            "-V",
            f"reportname={report_name}",
            "-N",
            "-f",
            "markdown+tex_math_dollars",
            "index_transformed.md",
            "-o",
            f"{report_name}.tex",
        ]
    )
    sp.call(["latexmk","-lualatex",f"{report_name}.tex"])
    os.remove("index_transformed.md")


if __name__ == "__main__":
    report_name = sys.argv[1]
    if report_name.endswith("/"):
        report_name = report_name[:-1]
    cwd = os.getcwd()
    os.chdir(report_name)
    build_report(report_name)
    os.rename(report_name+".pdf", "../"+report_name+".pdf")
    os.chdir(cwd)
