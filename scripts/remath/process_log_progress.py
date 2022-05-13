

def load_log_progress_file(filepath):
    vals = list()
    with open(filepath, 'r') as fin:
        vals = [int(line.strip('\n')) for line in fin.readlines()]
    return vals


values = load_log_progress_file('log_progress.txt')

print(f'number of values: {len(values)}')
print(f'max value:        {max(values)}')
