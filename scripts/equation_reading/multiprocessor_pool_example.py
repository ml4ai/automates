import time
import multiprocessing
from subprocess import call


lock = None  # Global definition of lock


def run_individual(params):
    global lock

    start_time = time.time()

    # any logging to a single log file BEFORE individual run should be here...
    lock.acquire()
    print(f"task {params['num']} START at {start_time}")
    lock.release()

    # run individual
    time.sleep(2)  # This is just for demonstration purposes!
    ret = call(params['command'], shell=True)

    end_time = time.time()
    duration = end_time - start_time

    # any logging to a single log file AFTER individual run should be here...
    lock.acquire()
    print(f"task {params['num']} END at {end_time}, dur={duration}, ret={ret}")
    lock.release()

    return f'task {params["num"]} dur={duration}'


def run_batch(pool_size, parameters):
    global lock

    print(f'total cores available: {multiprocessing.cpu_count()}')
    print(f'using cores: {pool_size}')

    # create global lock
    lock = multiprocessing.Lock()

    p = multiprocessing.Pool(pool_size)
    results = p.map(run_individual, parameters)

    # print the results that were returned by each call to run_individual
    print("Batch done")
    for result in results:
        print(result)


# SCRIPT

EXAMPLE_PARAMS = list()
for i in range(20):
    EXAMPLE_PARAMS.append({'num': i, 'command': 'date +%s'})

print("TASKS:")
for task in EXAMPLE_PARAMS:
    print('    ', task)
print("----------")

num_cores = multiprocessing.cpu_count()
print(f"TOTAL number of CORES: {num_cores}")
cores_to_use = num_cores - 2

run_batch(cores_to_use, EXAMPLE_PARAMS)
