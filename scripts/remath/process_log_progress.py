

def load_log_progress_file(filepath):
    vals = list()
    with open(filepath, 'r') as fin:
        vals = [int(line.strip('\n')) for line in fin.readlines()]
    return vals


def process_log_progress(filepath):
    values = load_log_progress_file(filepath)
    print(f'{filepath}')
    print(f'  number of values: {len(values)}')
    print(f'  max value:        {max(values)}')
    return values


def process_batch(filepaths):
    all_values = list()
    for filepath in filepaths:
        all_values += process_log_progress(filepath)
    print(f'total : {len(all_values)}')


process_batch(['log_progress_1.txt',
               'log_progress_2.txt',
               'log_progress_3.txt',
               'log_progress_4.txt',
               'log_progress_5.txt'])


