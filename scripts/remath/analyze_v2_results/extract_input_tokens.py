import os
import ast
import pickle


example_filepath = '../data/corpus_v2_results/tokens_input/expr_v2_0008400__Linux-5.4.0-81-generic-x86_64-with-glibc2.31__gcc-10.1.0__tokens.txt'


def parse_tokens_input_file(filepath):
    tokens = None
    with open(filepath, 'r') as infile:
        lines = infile.readlines()
        name = filepath.split(os.sep)[-1].split('__')[0]
        tokens = ast.literal_eval(lines[0])

    # print(name, tokens)

    return name, tokens


def load_input_token_data(input_tokens_root):
    data = dict()
    for subdir, dirs, files in os.walk(input_tokens_root):
        for f in files:
            if f.endswith('__tokens.txt'):
                filepath = subdir + os.sep + f
                name, tokens = parse_tokens_input_file(filepath)
                data[name] = tokens
    return data


def main():
    # name, tokens = parse_tokens_input_file(example_filepath)
    data = load_input_token_data('tokens_input')
    with open('../data/corpus_v2_results/tokens_input_all.pickle', 'wb') as pfile:
        pickle.dump(data, pfile, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    main()
