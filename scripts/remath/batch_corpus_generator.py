from dataclasses import dataclass
import json
import os
import shutil
from pathlib import Path
import uuid
import platform
import subprocess
import gen_c_prog


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


# -----------------------------------------------------------------------------
# Load config
# -----------------------------------------------------------------------------

def missing_config_message():
    print("CONFIGURATION config.json")
    print("To use this script you must first create a file 'config.json'")
    print("with the following contents -- replace <path_to_ghidra_root> with the")
    print("appropriate absolute path within a string:")
    print("{")

    print("  \"corpus_root\": \"<str> overall root directory path for the corpus\"")
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


def try_execute(bin_filepath: str):
    pass


def log_failure(filename_c:str, reason: str):
    with open('failures.log', 'a') as logfile:
        logfile.write(f'{filename_c}: {reason}\n')


def try_generate(config: Config, i: int, sig_digits: int):
    num_str = f'{i}'.zfill(sig_digits)
    filename_base = f'{config.base_name}_{num_str}'
    filename_c = filename_base + '.c'

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
        gen_c_prog.gen_prog(filename_c)  # filepath_uuid_c)

        # compile candidate
        result, bin_filepath = try_compile(config=config, src_filepath=filename_c)  # filepath_uuid_c)

        if result.returncode != 0:
            print(f'FAILURE - COMPILE - {result.returncode}')
            log_failure(filename_c, f'compilation return {result}')
            subprocess.call(['cp ' + filename_c + ' ' + filename_uuid_c])
            continue

        # execute_candidate
        result = subprocess.run([f'./{bin_filepath}'], stdout=subprocess.PIPE)

        if result.returncode != 0:
            print(f'FAILURE - EXECUTE - {result.returncode}')
            log_failure(filename_c, f'execution return {result.returncode}')
            subprocess.call(['cp ' + filename_c + ' ' + filename_uuid_c])
            continue

        # run Ghidra
        command_list = \
            [ghidra_command, ghidra_project_dir, ghidra_project_name,
             '-import', bin_filepath,
             '-scriptPath', config.ghidra_script_root,
             '-postScript', config.ghidra_script_filename,
             '-deleteProject']
        result = subprocess.run(command_list, stdout=subprocess.PIPE)

        if result.returncode != 0:
            print(f'FAILURE - GHIDRA - {result.returncode}')
            log_failure(filename_c, f'ghidra return {result.returncode}')
            subprocess.call(['cp ' + filename_c + ' ' + filename_uuid_c])
            continue

        # tokenize CAST

        # tokenize instructions

        # if get this far, then success!
        success = True
        keep_going = False  # could also just break...

    if success:
        # copy files to respective locations
        print('Success')
    else:
        raise Exception(f"ERROR try_generate(): failed to generate a viable program after {attempt} tries.")


def main():
    config = load_config()

    # Create corpus root, but don't allow if directory already exists,
    # to prevent overwriting...
    for path in (config.corpus_root, config.stage_root, config.src_root,
                 config.cast_root, config.bin_root,
                 config.ghidra_instructions_root,
                 config.corpus_input_tokens_root,
                 config.corpus_output_tokens_root):
        Path(path).mkdir(parents=True, exist_ok=False)

    original_working_dir = os.getcwd()
    os.chdir(config.stage_root)
    for i in range(config.num_samples):
        try_generate(config=config, i=i, sig_digits=len(str(config.num_samples)))
    os.chdir(original_working_dir)


# -----------------------------------------------------------------------------
# TOP LEVEL SCRIPT
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
