import os
from pathlib import Path


# https://codeforwin.org/2017/08/list-data-types-c-programming.html
# https://www.geeksforgeeks.org/c-data-types/
TYPES = \
    {'ANY': ('int', 'long', 'long long',
             'float', 'double', 'long double'),
     'REAL_FLOATING': ('float', 'double'),
     'NON_FLOAT': ('int', 'long', 'long long')}


BIN_OPERATORS = \
    (('+', 'ANY', 'ANY', 'ANY'),
     ('-', 'ANY', 'ANY', 'ANY'),
     ('*', 'ANY', 'ANY', 'ANY'),
     ('/', 'ANY', 'ANY', 'ANY'),
     ('%', 'int', 'int', 'int'),
     # bitwise logical operators
     ('&', 'NON_FLOAT', 'NON_FLOAT', 'NON_FLOAT'),  # bitwise AND
     ('|', 'NON_FLOAT', 'NON_FLOAT', 'NON_FLOAT'),  # bitwise inclusive OR
     ('^', 'NON_FLOAT', 'NON_FLOAT', 'NON_FLOAT'),  # bitwise exclusive OR
     ('<<'))


def gen_prog() -> str:
    return ''


def gen_prog_batch(n=1):
    root_dir = 'small_programs'
    Path(root_dir).mkdir(parents=True, exist_ok=True)
    for i in range(n):
        sig_digits = len(str(n))
        filename = f'source_{i}.c'.zfill(sig_digits)
        filepath = os.path.join(root_dir, filename)
        prog_str = gen_prog()
        with open(filepath, 'w') as fout:
            fout.write(prog_str)


def main():
    gen_prog_batch(n=1)


if __name__ == "__main__":
    main()
