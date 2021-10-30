from typing import List
import sys
import os
import json
import uuid
import platform
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
import timeit

import gen_c_prog
from automates.program_analysis.GCC2GrFN.gcc_ast_to_cast import GCC2CAST
from batch_tokenize_instructions import TokenSet, extract_tokens_from_instr_file


CTTC_SCRIPT = '../../cast_to_token_cast.py'


@dataclass
class Config:
    corpus_root: str = ''
    num_samples: int = 1
    total_attempts: int = 1
    base_name: str = ''

    gcc: str = ''
    gcc_plugin_filepath: str = ''
    ghidra_root: str = ''
    ghidra_script_root: str = ''
    ghidra_script_filename: str = ''

    stage_root_name: str = ''
    stage_root: str = ''
    src_root_name: str = ''
    src_root: str = ''
    cast_root_name: str = ''
    cast_root: str = ''
    bin_root_name: str = ''
    bin_root: str = ''
    ghidra_instructions_root_name: str = ''
    ghidra_instructions_root: str = ''
    corpus_input_tokens_root_name: str = ''   # tokenized binary
    corpus_input_tokens_root: str = ''
    corpus_output_tokens_root_name: str = ''  # tCAST
    corpus_output_tokens_root: str = ''

    time_start: float = 0
    iteration_times: List[float] = field(default_factory=list)


# -----------------------------------------------------------------------------
# Load config
# -----------------------------------------------------------------------------

def missing_config_message():
    print("CONFIGURATION config.json")
    print("To use this script you must first create a file 'config.json'")
    print("with the following contents -- replace <path_to_ghidra_root> with the")
    print("appropriate absolute path within a string:")
    print("{")

    print("  \"corpus_root\": \"<str> absolute path to top-level root directory for the corpus\"")
    print("  \"num_samples\": \"<int> number of samples to generate\"")
    print("  \"total_attempts\": \"<int> total sequential attempts to generate a valid, executable program\"")
    print("  \"base_name\": \"<str> the program base name\"")

    print("  \"gcc\": \"<str> path to gcc\"")
    print("  \"gcc\": \"<str> path to gcc plugin\"")
    print("  \"ghidra_root\": \"<str> root directory path of ghidra\"")
    print("  \"ghidra_script_root\": \"<str> root directory path of ghidra plugin scripts\"")
    print("  \"ghidra_script_filename\": \"<str> filename of ghidra plugin script\""
          "  # e.g., ..../DumpInstructionsByFunction.py")

    print("  \"stage_root\": \"<str> name of directory root for staging"
          " (generate candidate, attempt compile, attempt execution)\"")
    print("  \"src_root\": \"<str> name of directory root for C source code>\"")
    print("  \"cast_root\": \"<str> name of directory root for CAST>\"")
    print("  \"bin_root\": \"<str> name of directory root for binaries>\"")
    print("  \"ghidra_instructions_root\": \"<str> name of directory root for "
          "ghidra instructions (ghidra_working_directory)>\"")

    print("  \"corpus_input_tokens_dir_root\": \"<str> name of directory root for "
          "corpus input tokens (tokenized binaries)\"")
    print("  \"corpus_output_tokens_dir_root\": \"<str>: name of directory root for "
          "corpus output tokens (.tcast)\"")

    print("  \"sample_program_flag\": \"<Boolean>: whether to generate programs\"")
    print("  \"sample_program_num_samples\": \"<int>: number of programs to generate\"")
    print("  \"sample_program_base_name\": \"<str>: base name of all generated programs\"")
    print("}")


def configure_paths(config):
    config.stage_root = os.path.join(config.corpus_root, config.stage_root_name)
    config.src_root = os.path.join(config.corpus_root, config.src_root_name)
    config.cast_root = os.path.join(config.corpus_root, config.cast_root_name)
    config.bin_root = os.path.join(config.corpus_root, config.bin_root_name)
    config.ghidra_instructions_root = os.path.join(config.corpus_root, config.ghidra_instructions_root_name)
    config.corpus_input_tokens_root = os.path.join(config.corpus_root, config.corpus_input_tokens_root_name)
    config.corpus_output_tokens_root = os.path.join(config.corpus_root, config.corpus_output_tokens_root_name)


def load_config():
    # verify config.json exists
    if not os.path.isfile('config.json'):
        missing_config_message()
        raise Exception("ERROR: config.json not found; see CONFIGURATION message")

    config = Config()

    with open('config.json', 'r') as json_file:
        cdata = json.load(json_file)
        missing_fields = list()
        if 'corpus_root' not in cdata:
            missing_fields.append('corpus_root')
        else:
            config.corpus_root = cdata['corpus_root']
        if 'num_samples' not in cdata:
            missing_fields.append('num_samples')
        else:
            config.num_samples = cdata['num_samples']
        if 'total_attempts' not in cdata:
            missing_fields.append('total_attempts')
        else:
            config.total_attempts = cdata['total_attempts']
        if 'base_name' not in cdata:
            missing_fields.append('base_name')
        else:
            config.base_name = cdata['base_name']

        if 'gcc' not in cdata:
            missing_fields.append('gcc')
        else:
            config.gcc = cdata['gcc']
        if 'gcc_plugin_filepath' not in cdata:
            missing_fields.append('gcc_plugin_filepath')
        else:
            config.gcc_plugin_filepath = cdata['gcc_plugin_filepath']
        if 'ghidra_root' not in cdata:
            missing_fields.append('ghidra_root')
        else:
            config.ghidra_root = cdata['ghidra_root']
        if 'ghidra_script_root' not in cdata:
            missing_fields.append('ghidra_script_root')
        else:
            config.ghidra_script_root = cdata['ghidra_script_root']
        if 'ghidra_script_filename' not in cdata:
            missing_fields.append('ghidra_script_filename')
        else:
            config.ghidra_script_filename = cdata['ghidra_script_filename']

        if 'stage_root_name' not in cdata:
            missing_fields.append('stage_root_name')
        else:
            config.stage_root_name = cdata['stage_root_name']
        if 'src_root_name' not in cdata:
            missing_fields.append('src_root_name')
        else:
            config.src_root_name = cdata['src_root_name']
        if 'cast_root_name' not in cdata:
            missing_fields.append('cast_root_name')
        else:
            config.cast_root_name = cdata['cast_root_name']
        if 'bin_root_name' not in cdata:
            missing_fields.append('bin_root_name')
        else:
            config.bin_root_name = cdata['bin_root_name']
        if 'ghidra_instructions_root_name' not in cdata:
            missing_fields.append('ghidra_instructions_root_name')
        else:
            config.ghidra_instructions_root_name = cdata['ghidra_instructions_root_name']

        if 'corpus_input_tokens_root_name' not in cdata:
            missing_fields.append('corpus_input_tokens_root_name')
        else:
            config.corpus_input_tokens_root_name = cdata['corpus_input_tokens_root_name']
        if 'corpus_output_tokens_root_name' not in cdata:
            missing_fields.append('corpus_output_tokens_root_name')
        else:
            config.corpus_output_tokens_root_name = cdata['corpus_output_tokens_root_name']

        if missing_fields:
            missing_config_message()
            missing_str = '\n  '.join(missing_fields)
            raise Exception("ERROR load_config(): config.json missing "
                            f"the following fields:\n  {missing_str}")

        configure_paths(config)

        return config


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def get_gcc_version(gcc_path):
    """
    Helper to extract the gcc version
    :param gcc_path: path to gcc
    :return: string representing gcc version
    """
    version_bytes = subprocess.check_output([gcc_path, '--version'])
    version_str = version_bytes.decode('utf-8')
    if 'clang' in version_str:
        clang_idx = version_str.find('clang')
        return version_str[clang_idx:version_str.find(')', clang_idx)], 'clang'
    else:
        return 'gcc-' + version_str.split('\n')[0].split(' ')[2], 'gcc'


def try_compile(config: Config, src_filepath: str):
    gcc_version, compiler_type = get_gcc_version(config.gcc)
    platform_name = platform.platform()
    binary_postfix = '__' + platform_name + '__' + gcc_version

    dst_filepath = os.path.splitext(src_filepath)[0] + binary_postfix

    # print('try_compile() cwd:', os.getcwd())

    command_list = [config.gcc, f'-fplugin={config.gcc_plugin_filepath}', '-C', '-x', 'c++', '-O0', src_filepath, '-o', dst_filepath]
    print(command_list)

    result = subprocess.run(command_list, stdout=subprocess.PIPE)

    return result, dst_filepath


def gcc_ast_to_cast(filename_base: str, verbose_p: bool = False):
    ast_filename = filename_base + '_gcc_ast.json'
    ast_json = json.load(open(ast_filename))
    if verbose_p:
        print("Translate GCC AST into CAST:")
    cast = GCC2CAST([ast_json]).to_cast()
    cast_filename = filename_base + '--CAST.json'
    json.dump(cast.to_json_object(), open(cast_filename, "w"))
    return ast_filename, cast_filename


def log_failure(filename_c:str, reason: str):
    with open('failures.log', 'a') as logfile:
        logfile.write(f'{filename_c}: {reason}\n')


def finalize(config: Config, token_set: TokenSet):
    token_set_summary_filepath = os.path.join(config.stage_root, 'tokens_summary.txt')
    original_stdout = sys.stdout
    time_end = timeit.default_timer()
    total_time = config.time_start - time_end
    with open(token_set_summary_filepath, 'w') as fout:
        sys.stdout = fout
        token_set.print()
        print(f'total time: {config.time_start} {time_end} {total_time}')
        print('iteration_times:')
        print(config.iteration_times)
        sys.stdout = original_stdout


def try_generate(config: Config, i: int, sig_digits: int, token_set: TokenSet):

    time_start = timeit.default_timer()

    num_str = f'{i}'.zfill(sig_digits)
    filename_base = f'{config.base_name}_{num_str}'
    filename_src = filename_base + '.c'
    filename_bin = ''
    filename_gcc_ast = ''
    filename_cast = ''
    filename_ghidra_instructions = ''
    filename_tokens_output = ''

    attempt = 0
    keep_going = True
    success = False

    ghidra_command = os.path.join(config.ghidra_root, 'support/analyzeHeadless')
    ghidra_project_name = 'temp_ghidra_project'
    ghidra_project_dir = '.'

    while keep_going:

        # stop if have exceeded total_attempts
        if attempt >= config.total_attempts:
            break

        attempt += 1

        temp_uuid = str(uuid.uuid4())
        filename_base_uuid = f'{filename_base}_{temp_uuid}'
        filename_uuid_c = filename_base_uuid + '.c'

        # generate candidate source code
        gen_c_prog.gen_prog(filename_src)  # filepath_uuid_c)

        # compile candidate
        result, filename_bin = try_compile(config=config, src_filepath=filename_src)  # filepath_uuid_c)

        if result.returncode != 0:
            print(f'FAILURE - COMPILE - {result.returncode}')
            log_failure(filename_src, f'compilation return {result}')
            subprocess.call(['cp ' + filename_src + ' ' + filename_uuid_c])
            continue

        # execute_candidate
        result = subprocess.run([f'./{filename_bin}'], stdout=subprocess.PIPE)

        if result.returncode != 0:
            print(f'FAILURE - EXECUTE - {result.returncode}')
            log_failure(filename_src, f'execution return {result.returncode}')
            subprocess.call(['cp ' + filename_src + ' ' + filename_uuid_c])
            continue

        # gcc ast to CAST
        filename_gcc_ast, filename_cast = gcc_ast_to_cast(filename_base)

        # run Ghidra
        filename_ghidra_instructions = filename_bin + '-instructions.txt'
        command_list = \
            [ghidra_command, ghidra_project_dir, ghidra_project_name,
             '-import', filename_bin,
             '-scriptPath', config.ghidra_script_root,
             '-postScript', config.ghidra_script_filename,
             '-deleteProject']
        result = subprocess.run(command_list, stdout=subprocess.PIPE)

        if result.returncode != 0:
            print(f'FAILURE - GHIDRA - {result.returncode}')
            log_failure(filename_src, f'ghidra return {result.returncode}')
            subprocess.call(['cp ' + filename_src + ' ' + filename_uuid_c])
            continue

        # tokenize CAST
        filename_tokens_output = filename_base + '--CAST.tcast'
        result = subprocess.run(['python', CTTC_SCRIPT, '-f', filename_cast], stdout=subprocess.PIPE)

        if result.returncode != 0:
            print(f'FAILURE - cast_to_token_cast.py - {result.returncode}')
            log_failure(filename_src, f'cast_to_token_cast return {result.returncode}')
            subprocess.call(['cp ' + filename_src + ' ' + filename_uuid_c])
            continue

        # if get this far, then success!
        success = True
        keep_going = False  # could also just break...

    if success:
        # extract bin input tokens from ghidra instructions
        filename_bin_tokens = f'{config.corpus_input_tokens_root}/{filename_bin}__tokens.txt'
        extract_tokens_from_instr_file(token_set=token_set,
                                       _src_filepath=filename_ghidra_instructions,
                                       _dst_filepath=filename_bin_tokens,
                                       execute_p=True,
                                       verbose_p=False)

        # move files to respective locations:
        mv_files(config, token_set,
                 filename_src, filename_bin, filename_gcc_ast,
                 filename_cast, filename_ghidra_instructions,
                 filename_tokens_output)

        # Update the counter file
        with open('counter.txt', 'w') as counter_file:
            counter_file.write(f'{i}, {sig_digits}')
        print('Success')

        time_end = timeit.default_timer()
        time_elapsed = time_end - time_start
        with open('iteration_times.txt', 'a') as it_file:
            it_file.write(f'{time_elapsed} ')
        config.iteration_times.append(time_elapsed)
    else:
        time_end = timeit.default_timer()
        time_elapsed = time_end - time_start
        with open('iteration_times.txt', 'a') as it_file:
            it_file.write(f'{time_elapsed} ')
        config.iteration_times.append(time_elapsed)
        finalize(config, token_set)  # save current token_set before bailing
        raise Exception(f"ERROR try_generate(): failed to generate a viable program after {attempt} tries.")


def mv_files(config, token_set,
             filename_src, filename_bin, filename_gcc_ast,
             filename_cast, filename_ghidra_instructions,
             filename_tokens_output):
    filenames = (filename_src, filename_bin, filename_gcc_ast,
                 filename_cast, filename_ghidra_instructions,
                 filename_tokens_output)
    dest_paths = (config.src_root, config.bin_root, config.cast_root,
                  config.cast_root, config.ghidra_instructions_root,
                  config.corpus_output_tokens_root)
    for src_filename, dest_path in zip(filenames, dest_paths):
        dest_filepath = os.path.join(dest_path, src_filename)
        result = subprocess.run(['mv', src_filename, dest_filepath], stdout=subprocess.PIPE)
        if result.returncode != 0:
            finalize(config, token_set)
            raise Exception(f"ERROR mv_files(): failed mv {src_filename} --> {dest_filepath}\n"
                            f"  current directory: {os.getcwd()}")


def main(start=0):
    config = load_config()

    config.time_start = timeit.default_timer()

    # Create corpus root, but don't allow if directory already exists,
    # to prevent overwriting...
    for path in (config.corpus_root, config.stage_root, config.src_root,
                 config.cast_root, config.bin_root,
                 config.ghidra_instructions_root,
                 config.corpus_input_tokens_root,
                 config.corpus_output_tokens_root):
        Path(path).mkdir(parents=True, exist_ok=False)

    token_set = TokenSet()

    original_working_dir = os.getcwd()
    os.chdir(config.stage_root)

    # verify that we can find cast_to_token_cast.py script
    print(f'CWD: {os.getcwd()}')
    if os.path.isfile(CTTC_SCRIPT):
        print(f"Found cast_to_token_cast.py: {CTTC_SCRIPT}")
    else:
        raise Exception(f"ERROR: Cannot find cast_to_token_cast.py: {CTTC_SCRIPT}")

    for i in range(start, config.num_samples):
        try_generate(config=config, i=i,
                     sig_digits=len(str(config.num_samples)),
                     token_set=token_set)
    finalize(config, token_set)
    os.chdir(original_working_dir)


# -----------------------------------------------------------------------------
# TOP LEVEL SCRIPT
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
