import argparse


def clean_line(line):
    tokens = list()
    for token in line.strip('\n').strip('\\').strip(' ').split(' '):
        for tstrips in ('\\', '&'):
            token = token.strip(tstrips)
        if token != '':
            tokens.append(token)
    return ' '.join(tokens)


def process_markdown(filepath, outfile):
    math_envs = list()
    in_math_p = False
    with open(filepath, 'r') as fin:
        for line in fin.readlines():
            if in_math_p and "```" in line:
                in_math_p = False
            elif "```math" in line:
                in_math_p = True
            else:
                if in_math_p and "\\begin" not in line and "\\end" not in line:
                    math_envs.append(clean_line(line))
    if outfile:
        with open(outfile, 'w') as fout:
            for line in math_envs:
                fout.write(line + '\n')
    else:
        for line in math_envs:
            print(line)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='README.md',
                        help='Input filepath. (Default: README.md)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output filepath. (When not specified: Print to stdout)')
    args = parser.parse_args()
    process_markdown(args.input, args.output)


if __name__ == '__main__':
    main()
