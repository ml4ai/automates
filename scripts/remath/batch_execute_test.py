import subprocess


def execute(filepath):
    result = subprocess.run(filepath, stdout=subprocess.PIPE)
    if result.returncode != 0:
        print('exec failed!')
    else:
        print('exec succeeded!')


if __name__ == '__main__':
    execute('examples_bin/gcc/expr_07__Linux-5.11.0-38-generic-x86_64-with-glibc2.31__gcc-10.1.0')
