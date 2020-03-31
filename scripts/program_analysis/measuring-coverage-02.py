#!/usr/bin/env python

""" This file contains code to carry out a simple estimate of the amount of
    Fortran code 'handled' by for2py.

    COMMAND-LINE INVOCATION:

        ./measure-coverage.py <directory with Fortran code files>


    ADDING HANDLED LANGUAGE CONSTRUCTS:
    As the set of language features handled by for2py grows, they should be
    incorporated into this script.  This can be done as follows:

    1) Write a regular expression to recognize that feature (see examples
       under "SYNTAX MATCHING" below).

    2) Add the regular expression to the list for the variable HANDLED.
"""

import os
import sys
import json
from pathlib import Path
import logging
import argparse
from tqdm import tqdm
from itertools import chain
from future.utils import lmap
from utils.fp import flatten, pairwise
from program_analysis.for2py import preprocessor
from program_analysis.for2py.syntax import *
from pygraphviz import AGraph
import matplotlib
from matplotlib import cm

# Check Python version - the script needs Python 3.6 or 3.7.

assert sys.version_info.major == 3 and sys.version_info.minor in (6, 7)

FORTRAN_EXTENSIONS = {".f", ".f90", ".for"}

# ------------------------------------------------------------------------------
# HACK
# ------------------------------------------------------------------------------

# Global to keep track of file with largest number of lines
LINES_MAX = 0
LINES_MAX_FILE = ''

LINES_MIN = 99999999999
LINES_MIN_FILE = ''

LINES_MAX_DSSAT = 9327

# Mini-SPAM
SPAM = \
    ('ETPHOT.for', 'ROOTWU.for', 'SPAM.for', 'STEMP.for', 'ETPHR.for',
     'PET.for', 'SOILEV.for', 'SPSUBS.for', 'TRANS.for',  # SPAM
     'MULCH_EVAP.for',  # Soil/Mulch
     'DATES.for', 'ModuleDefs.for', 'WARNING.for',  # Utilities
     'HMET.for'  # Weather
     )

# dssat_PET
PET = \
    ('ERROR.for', 'Paddy_Mgmt.for', 'ROOTWU.for', 'VEGDM.for', 'CSMVersion.for',
     'ESR_SOILEVAP.for', 'RESPIR.for', 'diffusiv.for', 'ASMDM.for', 'MULCHEVAP.for',
     'TextureClass.for', 'NFLUX.for', 'SDCOMP.for', 'VEGDM.for', 'SOLAR.for',
     'MOBIL.for', 'RNOFF.for', 'OSDefinitions.for', 'nox_pulse.for', 'plant.for',
     'RStages.for', 'Flood_Irrig.for')


# ------------------------------------------------------------------------------
# END HACK
# ------------------------------------------------------------------------------


################################################################################
#                                                                              #
#                                SYNTAX MATCHING                               #
#                                                                              #
################################################################################

# Regular expressions that specify patterns for various Fortran constructs.
# These are very similar to the constructs in the file syntax.py, but only
# include constructs that are currently handled in for2py.

FN_START = r"\s*(\w*\s*){0,2}function\s+(\w+)\s*\("
RE_FN_START = re.compile(FN_START, re.I)

PGM_UNIT = (
    r"\s*\w*\s*(program|module|subroutine|(\w*\s*){0,2}function)\s+(\w+)"
)
RE_PGM_UNIT_START = re.compile(PGM_UNIT, re.I)

PGM_UNIT_SEP = r"\s+contains(\W+)"
RE_PGM_UNIT_SEP = re.compile(PGM_UNIT_SEP, re.I)

PGM_UNIT_END = r"\s*[a-z]*\s*end\s+(program|module|subroutine|function)\s+"
RE_PGM_UNIT_END = re.compile(PGM_UNIT_END, re.I)

SUBPGM_END = r"\s*end\s+"
RE_SUBPGM_END = re.compile(SUBPGM_END, re.I)

ASSG_STMT = r"\s*(\d+|&)?\s*.*=\s*"
RE_ASSG_STMT = re.compile(ASSG_STMT, re.I)

IMPLICIT_STMT = r"\s*implicit\s+"
RE_IMPLICIT_STMT = re.compile(IMPLICIT_STMT, re.I)

CALL_STMT = r"\s*(\d+|&)?\s*call\s*"
RE_CALL_STMT = re.compile(CALL_STMT, re.I)

IO_STMT = r"\s*(\d+|&)?\s*(open|close|read|write|print|format|rewind)\W*"
RE_IO_STMT = re.compile(IO_STMT, re.I)

DO_STMT = r"\s*(\d+|&)?\s*do\s*"
RE_DO_STMT = re.compile(DO_STMT, re.I)

ENDDO_STMT = r"\s*(\d+|&)?\s*end\s*do\s*"
RE_ENDDO_STMT = re.compile(ENDDO_STMT, re.I)

ENDIF_STMT = r"\s*(\d+|&)?\s*end\s*if\s*"
RE_ENDIF_STMT = re.compile(ENDIF_STMT, re.I)

GOTO_STMT = r"\s*(\d+|&)?\s*go\s*to\s*"
RE_GOTO_STMT = re.compile(GOTO_STMT, re.I)

IF_STMT = r"\s*(\d+|&)?\s*(if|elseif|else)\s*"
RE_IF_STMT = re.compile(IF_STMT, re.I)

INCLUDE_STMT_1 = r"\s*(\d+)?\s*include\s+'(\w+(\.\w*)?)'"
RE_INCLUDE_STMT_1 = re.compile(INCLUDE_STMT_1, re.I)
INCLUDE_STMT_2 = r'\s*(\d+)?\s*include\s+"(\w+(\.\w*)?)"'
RE_INCLUDE_STMT_2 = re.compile(INCLUDE_STMT_2, re.I)

PAUSE_STMT = r"\s*(\d+|&)?\s*pause\s*"
RE_PAUSE_STMT = re.compile(PAUSE_STMT, re.I)

USE_STMT = r"\s*(\d+|&)?\s*use\s*\,*([a-z0-9_\-]+)"
RE_USE_STMT = re.compile(USE_STMT, re.I)

RETURN_STMT = r"\s*(\d+|&)?\s*return\s*"
RE_RETURN_STMT = re.compile(RETURN_STMT, re.I)

CYCLE_STMT = r"\s*(\d+|&)?\s*cycle\s*"
RE_CYCLE_STMT = re.compile(CYCLE_STMT, re.I)

EXIT_STMT = r"\s*(\d+|&)?\s*exit\s*"
RE_EXIT_STMT = re.compile(EXIT_STMT, re.I)

SAVE_STMT = r"\s*(\d+|&)?\s*save\s*"
RE_SAVE_STMT = re.compile(SAVE_STMT, re.I)

SELECT_STMT = r"\s*(\d+|&)?\s*select\s*case\s*"
RE_SELECT_STMT = re.compile(SELECT_STMT, re.I)

ENDSELECT_STMT = r"\s*(\d+|&)?\s*end\s*select\s*"
RE_ENDSELECT_STMT = re.compile(ENDSELECT_STMT, re.I)

CASE_STMT = r"\s*(\d+|&)?\s*case\s*"
RE_CASE_STMT = re.compile(CASE_STMT, re.I)

STOP_STMT = r"\s*(\d+|&)?\s*stop\s*"
RE_STOP_STMT = re.compile(STOP_STMT, re.I)

DATA_STMT = r"\s*(\d+|&)?\s*data\s*(.*?)\/(.*?)\/"
RE_DATA_STMT = re.compile(DATA_STMT, re.I)

INTERAFCE_STMT = r"\s*(\d+|&)?\s*interface\s*"
RE_INTERAFCE_STMT = re.compile(INTERAFCE_STMT, re.I)

END_STMT = r"\s*(\d+|&)?\s*end\s*$"
RE_END_STMT = re.compile(END_STMT, re.I)

TYPE_NAMES = (
    r"^\s*(integer|real|double\s+precision|logical|dimension|type"
    r"|character)\W*"
)
RE_TYPE_NAMES = re.compile(TYPE_NAMES, re.I)

HANDLED = [
    RE_FN_START,
    RE_PGM_UNIT_START,
    RE_PGM_UNIT_SEP,
    RE_PGM_UNIT_END,
    RE_SUBPGM_END,
    RE_ASSG_STMT,
    RE_CALL_STMT,
    RE_CYCLE_STMT,
    RE_EXIT_STMT,
    RE_IMPLICIT_STMT,
    RE_INCLUDE_STMT_1,
    RE_INCLUDE_STMT_2,
    RE_IO_STMT,
    RE_DO_STMT,
    RE_ENDDO_STMT,
    RE_ENDIF_STMT,
    RE_GOTO_STMT,
    RE_IF_STMT,
    RE_PAUSE_STMT,
    RE_RETURN_STMT,
    RE_SAVE_STMT,
    RE_STOP_STMT,
    RE_TYPE_NAMES,
    RE_USE_STMT,
    RE_DATA_STMT,
    RE_SELECT_STMT,
    RE_ENDSELECT_STMT,
    RE_CASE_STMT,
    RE_INTERAFCE_STMT,
    RE_END_STMT,
]

KEYWD = r"\s*(\d+|&)?\s*\,*\s*([a-z0-9]+).*"
RE_KEYWD = re.compile(KEYWD)


def line_is_handled(filename, line):
    unhandled_keywds, unhandled_lines, used_modules = set(), set(), set()

    # Try to find the first keyword in the line
    match = RE_KEYWD.match(line.strip().lower())
    if match is not None:
        first_wd = match.group(2)
    else:
        first_wd = None

    # Try to match the line to the regex of a handled Fortran construct. If
    # matches, return with a True flag
    for handled_construct in HANDLED:
        if handled_construct.match(line) is not None:
            if handled_construct == RE_USE_STMT:
                match = handled_construct.match(line)
                used_modules.add(match.group(2))
            return True, unhandled_keywds, unhandled_lines, used_modules

    # For lines that contain unhandled constructs, check whether they contain
    # actual Fortran keywords or are just simple Fortran code lines
    if first_wd in F_KEYWDS:
        unhandled_keywds.add(first_wd)
    else:
        unhandled_lines.add((filename, line))

    return False, unhandled_keywds, unhandled_lines, used_modules


################################################################################
#                                                                              #
#                                FILE PROCESSING                               #
#                                                                              #
################################################################################


def get_code_lines(filename):
    """
        This function performs the pre-processing of the Fortran file and
        returns a list of code lines contained in the file
    """
    logging.debug("@@@ FILE: " + filename)
    return preprocessor.get_preprocessed_lines_from_file(filename)


def process_lines(filename, lines):
    """
        This function processes a list of code lines one by one, aggregating
        the results from each one
    """
    handled_files = 1
    unhandled_keywds = {}
    unhandled_lines = set()
    used_modules = set()
    nlines = len(lines)
    nhandled = 0
    for line in lines:
        handled, u_keywds, u_lines, u_modules = line_is_handled(filename, line)
        if handled:
            nhandled += 1
            used_modules |= u_modules
        else:
            handled_files = 0
            unhandled_lines |= u_lines
            for keywd in u_keywds:
                if keywd in unhandled_keywds:
                    unhandled_keywds[keywd] += 1
                else:
                    unhandled_keywds[keywd] = 1

    return (
        nlines,
        nhandled,
        unhandled_keywds,
        unhandled_lines,
        handled_files,
        used_modules,
    )


def process_file(filename):
    """
        This function processes one individual Fortran file and returns the
        results obtained from it.
    """
    # Get a list of pre-processed lines contained within the file
    code_lines = get_code_lines(filename)
    # Process these code lines one by one and get the results
    results = process_lines(filename, code_lines)
    return results


def process_dir(dirname, G):
    """
        This function recursively processes all the contents of a single
        directory

        TODO: Currently has bug where nfiles returns 0
    """

    # TODO HACK
    global LINES_MAX, LINES_MIN, LINES_MAX_FILE, LINES_MIN_FILE

    # Variable initializations
    unhandled_keywds, unhandled_lines = {}, set()
    file_map = {}
    nfiles, ntot, nhandled, handled_files = 0, 0, 0, 0

    # Get the full path of the directory
    logging.debug(f"processing: {dirname}")

    # Get a list of all the contents inside `dirname`

    # Get a list of all the contents inside `dirname`
    abs_path = os.path.abspath(dirname)
    list_of_files = os.listdir(dirname)
    files_to_link = []
    # Iterate through each file one by one
    cluster_name = str(Path(dirname).stem)
    G.add_subgraph(
        [], f"cluster_{cluster_name}", label=cluster_name, rankdir="TB",
    )
    subgraph = G.get_subgraph(f"cluster_{cluster_name}")

    for fname in list_of_files:
        full_path_to_file = abs_path + "/" + fname
        # Check if the file is a directory. If it is, recursively call this
        # function within this directory first
        if os.path.isdir(full_path_to_file):
            nf1, nt1, nh1, uk1, ul1, hf, fmap = process_dir(full_path_to_file, subgraph)
            # Add the result of this directory to the total counters
            nfiles += nf1
            ntot += nt1
            nhandled += nh1
            handled_files += hf
            for keywd in uk1:
                if keywd in unhandled_keywds:
                    unhandled_keywds[keywd] += uk1[keywd]
                else:
                    unhandled_keywds[keywd] = uk1[keywd]

            unhandled_lines |= ul1
            file_map.update(fmap)
        else:
            # If this is a file, get the file extension and check if it is
            # supported by this script
            _, fext = os.path.splitext(fname)
            if fext in FORTRAN_EXTENSIONS:
                # Process the contents of the file and get the results
                ftot, fhandled, u_keywds, u_lines, h_files, u_modules = \
                    process_file(full_path_to_file)
                # Add the result to the total counters
                ntot += ftot
                nhandled += fhandled
                handled_files += h_files

                for keywd in u_keywds:
                    if keywd in unhandled_keywds:
                        unhandled_keywds[keywd] += u_keywds[keywd]
                    else:
                        unhandled_keywds[keywd] = u_keywds[keywd]
                unhandled_lines |= u_lines
                if ftot == 0:
                    logging.debug(f"Ignoring {full_path_to_file} [file is empty]")
                    continue
                else:
                    pct_handled = fhandled / ftot * 100

                # TODO HACK: finding the file with the largest number of lines
                if ftot > LINES_MAX:
                    LINES_MAX = ftot
                    LINES_MAX_FILE = fname
                if ftot < LINES_MIN:
                    LINES_MIN = ftot
                    LINES_MIN_FILE = fname

                node_size = ftot / LINES_MAX_DSSAT

                color = (
                    matplotlib.colors.rgb2hex(cm.Greens(pct_handled / 100.0))
                    # matplotlib.colors.rgb2hex(cm.Greens(node_size))
                )

                if fname in PET:
                    color = 'red'
                else:
                    color = 'black'

                node_name = f'{fname} ({ftot})'

                # G.add_node(node_name, style="filled", fontcolor="white", fillcolor=color)
                # G.add_node(fname, width=node_size, style="filled", fontcolor="white", fillcolor=color)
                G.add_node(fname, style="filled", fontcolor="white", fillcolor=color)

                file_map[fname] = {
                    "Total number of lines": ftot,
                    "Number of lines handled": fhandled,
                    "Percentage of file handled": f"{pct_handled:.1f}%",
                    "Imported modules": list(u_modules),
                    "Unhandled keywords": u_keywds,
                    "Unhandled lines": [line[1] for line in list(u_lines)],
                }

                file_path_key = Path(full_path_to_file).relative_to(Path(dirname).parent)
                file_map[str(file_path_key)] = {
                    "Total number of lines": ftot,
                    "Number of lines handled": fhandled,
                    "Percentage of file handled": f"{pct_handled:.1f}%",
                    "Imported modules": list(u_modules),
                    "Unhandled keywords": u_keywds,
                    "Unhandled lines": [line[1] for line in list(u_lines)],
                }
                files_to_link.append(fname)
        for f1, f2 in pairwise(files_to_link):
            subgraph.add_edge(f1, f2, color="white")

    return (
        nfiles,
        ntot,
        nhandled,
        unhandled_keywds,
        unhandled_lines,
        handled_files,
        file_map,
    )


def print_results(results):
    nfiles, ntot, nhandled, u_keywds, u_lines, h_files, file_map = results

    if nfiles > 0:
        pct_handled = h_files / nfiles * 100
    else:
        pct_handled = 0

    logging.debug(
        f"FILES: total = {nfiles}; handled = {h_files} "
        f"[{pct_handled:.1f}%]\n"
    )

    if ntot > 0:
        pct_handled = nhandled / ntot * 100
    else:
        pct_handled = 0

    logging.debug(
        f"LINES: total = {ntot}; handled = {nhandled} [{pct_handled:.1f}%]\n"
    )

    if u_keywds != set():
        logging.debug("UNHANDLED KEYWORDS:")
        logging.debug("------------------")
        for item in u_keywds:
            logging.debug(f"    {item} : {u_keywds[item]}")

    if u_lines != set():
        logging.debug("UNHANDLED LINES:")
        logging.debug("---------------")
        for item in u_lines:
            logging.debug(f"    {item}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Measure for2py coverage of a directory."
    )
    parser.add_argument("directory", help="The directory to process")
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    file_map = {}
    G = AGraph(rankdir="TB")
    G.node_attr["shape"] = "rectangle"
    G.node_attr["style"] = "rounded"
    G.node_attr["fontname"] = "Menlo"
    results = process_dir(Path(args.directory).resolve(), G)
    G.draw("coverage_map.pdf", prog="dot")

    coverage_results_dict = results[-1]

    # with open("coverage_file_map.json", "w") as fp:
        # json.dump(coverage_results_dict, fp, indent=4)

    # TODO: Hack to work around nfile (first value in _result_ from process_dir()) ending up as 0.
    temp_nfile = [results[0]]
    results = tuple([G.number_of_nodes(), *results[1:]])
    print_results(results)
    print(f'TODO BUG (nfile returning 0): nfile= {temp_nfile}')
    print(f'LINES_MIN: {LINES_MIN_FILE} {LINES_MIN}')
    print(f'LINES_MAX: {LINES_MAX_FILE} {LINES_MAX}')
