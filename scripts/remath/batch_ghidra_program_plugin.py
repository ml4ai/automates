import os
import subprocess
import pathlib
import json
import argparse
import timeit


def run_ghidra(ghidra_root='', binary_root_dir='', binary_file='', working_root_dir='',
               script_root_dir='', script='',
               execute_p=False):

    # create destination root directory if does not already exist
    pathlib.Path(working_root_dir).mkdir(parents=True, exist_ok=True)

    original_working_dir = os.getcwd()
    os.chdir(working_root_dir)
    print(f'Working directory: {os.getcwd()}')

    # the project name is required but this will be deleted after processing,
    # so not super important
    project_name = 'temp_ghidra_project'
    projects_dir = '.'  # same as current working directory (working_root_dir)

    errors = list()

    def execute(filepath):
        ghidra_command = os.path.join(ghidra_root, 'support/analyzeHeadless')
        # script_path = os.path.join(script_root_dir, script)
        command_list = [ghidra_command, projects_dir, project_name,
                        '-import', filepath,
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

    times = list()

    # TODO: handle case of binary_file, which means don't process whole binary root dir
    if binary_file != '':
        bin_filepath = os.path.join(binary_root_dir, binary_file)
        start_time = timeit.default_timer()
        execute(bin_filepath)
        end_time = timeit.default_timer()
        times.append(end_time - start_time)
    else:
        # iterate through the src_root_dir
        for subdir, dirs, files in os.walk(binary_root_dir):
            for file in files:
                bin_filepath = subdir + os.sep + file
                start_time = timeit.default_timer()
                execute(bin_filepath)
                end_time = timeit.default_timer()
                times.append(end_time - start_time)


    os.chdir(original_working_dir)

    return errors, times


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
                        help='execute script (as opposed to running in test mosde)',
                        action='store_true', default=False)
    parser.add_argument('-w', '--working_root_dir',
                        help='specify the working directory root',
                        type=str,
                        default='examples_ghidra_instructions')
    parser.add_argument('-S', '--script_root_dir',
                        help='specify the Ghidra script root directory (relative to working directory root)',
                        type=str,
                        default='../../ghidra')
    parser.add_argument('-s', '--script_file',
                        help='specify specific Ghidra plugin script to run',
                        type=str,
                        default='DumpInstructionsByFunction.py')
    parser.add_argument('-B', '--binary_root_dir',
                        help='specify the binaries root directory (relative to working directory root)',
                        type=str,
                        default='')
    parser.add_argument('-b', '--binary_file',
                        help='Optionally specify a specific file to process; '
                             'if left unspecified, then processes whole directory',
                        type=str,
                        default='')
    args = parser.parse_args()
    if args.execute:
        print(f'EXECUTE! {args.working_root_dir} {args.script_root_dir} {args.script_file} {args.binary_root_dir}')
    else:
        print(f'Running in TEST mode {args.working_root_dir} {args.script_root_dir} {args.script_file} {args.binary_root_dir}')

    # verify config.json exists
    if not os.path.isfile('config.json'):
        config_requirement_message()
        return

    # get ghidra_path
    ghidra_root = ''
    with open('config.json', 'r') as json_file:
        data = json.load(json_file)
        if 'ghidra' not in data:
            print("config.json must specify field 'ghidra'")
            return
        ghidra_root = data['ghidra']
        print(f"ghidra root: {ghidra_root}")

    errors, times = \
        run_ghidra(ghidra_root=ghidra_root,
                   binary_root_dir=args.binary_root_dir,
                   binary_file=args.binary_file,
                   working_root_dir=args.working_root_dir,
                   script_root_dir=args.script_root_dir,
                   script=args.script_file,
                   execute_p=args.execute)
    for e in errors:
        print(f'ERROR: {e}')
    print(f'run times: {times}')


if __name__ == '__main__':
    # python batch_ghidra_program_plugin.py -B ../examples_bin/Linux -b add_int_printf_03__Linux-5.11.0-37-generic-x86_64-with-glibc2.31__gcc-10.1.0
    # python batch_ghidra_program_plugin.py -s EnumerateFunctions.py -w examples_ghidra_functions -B ../examples_bin/Darwin -e
    main()
