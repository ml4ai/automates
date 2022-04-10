from dataclasses import dataclass
from typing import List
import json
import batch_ghidra_program_plugin as ghidra
import batch_tokenize_instructions as tokenize

"""
A stand-alone script that iterates through a list of binary
  filenames, calling Ghidra to extract instructions
  TODO: and then tokenizing the instructions.
"""


@dataclass
class Params:
    binary_files: List[str]
    binary_root_dir: str
    working_root_dir: str
    script_file: str
    script_root_dir: str


PARAMS_1 = Params(
    binary_files=['math_sqrt_int',
                  'math_sqrt_int_global',
                  'math_sqrt_double_global',
                  'math_sqrt_double_x_z_global',
                  'sine+from_table'],
    binary_root_dir='data/example_c',
    working_root_dir='data/example_c',
    script_file='DumpInstructionsByFunction.py',
    script_root_dir='../../ghidra',
)


def run_ghidra_wrapper(ghidra_root,
                       binary_file: str,
                       binary_root_dir='data/example_c',
                       working_root_dir='',
                       script_file='DumpInstructionsByFunction.py',
                       script_root_dir='../../ghidra',
                       execute_p=False):
    errors, times = \
        ghidra.run_ghidra(ghidra_root=ghidra_root,
                          binary_root_dir=binary_root_dir,
                          binary_file=binary_file,
                          working_root_dir=working_root_dir,
                          script_root_dir=script_root_dir,
                          script=script_file,
                          execute_p=execute_p)
    for e in errors:
        print(f'ERROR: {e}')
    print(f'run times: {times}')


def main(params: Params,
         execute_p=False):

    # get ghidra_path
    with open('config.json', 'r') as json_file:
        data = json.load(json_file)
        if 'ghidra_root' not in data:
            print("config.json must specify field 'ghidra'")
            return
        ghidra_root = data['ghidra_root']
        print(f"ghidra root: {ghidra_root}")

    for binary_file in params.binary_files:
        run_ghidra_wrapper(ghidra_root,
                           binary_file,
                           params.binary_root_dir,
                           params.working_root_dir,
                           params.script_file,
                           params.script_root_dir,
                           execute_p)


if __name__ == "__main__":
    main(PARAMS_1)
