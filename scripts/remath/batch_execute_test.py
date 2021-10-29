import subprocess


def execute(filepath):
    result = subprocess.run(filepath, stdout=subprocess.PIPE)
    if result.returncode != 0:
        print('exec failed!')
    else:
        print('exec succeeded!')


if __name__ == '__main__':
    execute('examples_bin/gcc/')