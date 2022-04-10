# NOTE: This script executes Ghidra and extracts and dumps Unrefined and Refined PCode
# As of 2022-04-10: we are not yet using PCode, so this script is for exploratory purposes...

import os
import subprocess
import pathlib
import json
import argparse


def run_ghidra(ghidra_root='', binary_root_dir='', working_root_dir='', script_root_dir='', execute_p=False):
    # create destination root directory if does not already exist
    pathlib.Path(working_root_dir).mkdir(parents=True, exist_ok=True)

    original_working_dir = os.getcwd()
    os.chdir(working_root_dir)

    # the project name is required but this will be deleted after processing,
    # so not super important
    project_name = 'temp_ghidra_project'
    projects_dir = '.'  # same as current working directory (working_root_dir)

    errors = list()

    # iterate through the src_root_dir
    for subdir, dirs, files in os.walk(binary_root_dir):
        for file in files:
            for script in ('DumpRefined.py', 'DumpUnrefined.py'):
                bin_filepath = subdir + os.sep + file
                ghidra_command = os.path.join(ghidra_root, 'support/analyzeHeadless')
                # script_path = os.path.join(script_root_dir, script)
                command_list = [ghidra_command, projects_dir, project_name,
                                '-import', bin_filepath,
                                '-scriptPath', script_root_dir,
                                '-postScript', script,
                                '-deleteProject']
                if not execute_p:
                    print(command_list)
                else:
                    print(f'Executing {command_list}')
                    result = subprocess.run(command_list, stdout=subprocess.PIPE)
                    if result.returncode != 0:
                        errors.append(result)

    os.chdir(original_working_dir)

    return errors


def config_requirement_message():
    print("To use this script you must first create a file 'config.json'")
    print("with the following contents -- replace <path_to_ghidra_root> with the")
    print("appropriate absolute path within a string:")
    print("{")
    print("  \"ghidra\": \"<path_to_ghidra_root>\"")
    print("}")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--execute',
                        help='execute script (as opposed to running in test mode)',
                        action='store_true', default=False)
    parser.add_argument('-w', '--working_root_dir',
                        help='specify the working directory root',
                        type=str,
                        default='examples_ghidra')
    parser.add_argument('-s', '--script_root_dir',
                        help='specify the Ghidra script root directory',
                        type=str,
                        default='../../ghidra')
    parser.add_argument('-b', '--binary_root_dir',
                        help='specify the binaries root directory',
                        type=str,
                        default='../examples_bin')
    args = parser.parse_args()
    if args.execute:
        print(f'EXECUTE! {args.working_root_dir} {args.script_root_dir} {args.binary_root_dir}')
    else:
        print(f'Running in TEST mode {args.working_root_dir} {args.script_root_dir} {args.binary_root_dir}')

    # verify config.json exists
    if not os.path.isfile('config.json'):
        config_requirement_message()
        return

    # get ghidra_path
    with open('config.json', 'r') as json_file:
        data = json.load(json_file)
        if 'ghidra' not in data:
            print("config.json must specify field 'ghidra'")
            return
        ghidra_root = data['ghidra']
        print(f"ghidra root: {ghidra_root}")

    errors = run_ghidra(ghidra_root=ghidra_root,
                        binary_root_dir=args.binary_root_dir,
                        working_root_dir=args.working_root_dir,
                        script_root_dir=args.script_root_dir,
                        execute_p=args.execute)
    for e in errors:
        print(f'ERROR: {e}')


if __name__ == '__main__':
    main()
