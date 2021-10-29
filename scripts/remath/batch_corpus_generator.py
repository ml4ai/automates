from dataclasses import dataclass
import json
import os
from pathlib import Path
import gen_c_prog


@dataclass
class Config:
    corpus_root: str = ''

    gcc: str = ''
    ghidra_root: str = ''
    ghidra_script_filepath: str = ''

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

    sample_program_flag: bool = False
    sample_program_num_samples: int = 1
    sample_program_base_name: str = ''


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

    print("  \"gcc\": \"<str> path to gcc\"")
    print("  \"ghidra_root\": \"<str> root directory path of ghidra\"")
    print("  \"ghidra_script_filepath\": \"<str> path to ghidra plugin script\""
          "  # e.g., ..../DumpInstructionsByFunction.py")

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

        if 'gcc' not in cdata:
            missing_fields.append('gcc')
        else:
            config.gcc = cdata['gcc']
        if 'ghidra_root' not in cdata:
            missing_fields.append('ghidra_root')
        else:
            config.ghidra_root = cdata['ghidra_root']
        if 'ghidra_script_filepath' not in cdata:
            missing_fields.append('ghidra_script_filepath')
        else:
            config.ghidra_root = cdata['ghidra_script_filepath']

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

        # optional config
        if 'sample_program_flag' not in cdata:
            missing_fields.append('sample_program_flag')
        else:
            config.sample_program_flag = cdata['sample_program_flag']
        if 'sample_program_num_samples' not in cdata:
            missing_fields.append('sample_program_num_samples')
        else:
            config.sample_program_num_samples = cdata['sample_program_num_samples']
        if 'sample_program_base_name' not in cdata:
            missing_fields.append('sample_program_base_name')
        else:
            config.sample_program_base_name = cdata['sample_program_base_name']

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

def main():
    config = load_config()

    # Create corpus root, but don't allow if directory already exists,
    # to prevent overwriting...
    Path(config.corpus_root).mkdir(parents=True, exist_ok=False)

    if config.sample_program_flag:
        print(f'### Sampling programs: {config.sample_program_num_samples}')
        gen_c_prog.gen_prog_batch(n=config.sample_program_num_samples,
                                  root_dir=config.src_root,
                                  base_name=config.sample_program_base_name,
                                  verbose_p=True)


# -----------------------------------------------------------------------------
# TOP LEVEL SCRIPT
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
