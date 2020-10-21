import random
from subprocess import Popen, PIPE, TimeoutExpired

from multiprocessing import Pool, cpu_count, Lock


# Create a global lock to log results amongst the processes
LOG_LOCK = Lock()


def main():
    # This array will track process numbers and provide different amount of
    # sleep times to Python's time.sleep() method to exercise our ability to
    # catch timeout errors amongst the subprocesses.
    sleep_amounts = [(i + 1, random.randint(1, 9)) for i in range(20)]
    print(f"Testing sleep with:\n{sleep_amounts}")

    with Pool(cpu_count()) as pool:
        # Use a simple map to pass data to each process
        results = pool.map(sample_parallel_timeout, sleep_amounts)
        print(results)      # Verify that the results from map()


def sample_parallel_timeout(data):
    # Unpack the data for this process using standard python tuple unpacking
    (process_idx, sleep_time) = data

    # Notify the shell that we have started the current process
    LOG_LOCK.acquire()
    print(f"Starting process {process_idx}")
    LOG_LOCK.release()

    result = None
    seconds_till_timeout = 4    # Set the seconds to wait for a timeout
    try:
        # Include a sleep() in the command that will fail in some instances.
        # Also include a print portion from the shell to show output capture.
        test = [
            "python",
            "-c",
            f"import time;time.sleep({sleep_time});print('Process {process_idx}: {sleep_time} seconds')",
        ]
        # Create a new Process with the test command
        process = Popen(test, stdout=PIPE, stderr=PIPE)
        # Block this process while the subprocess completes
        # End the subprocess if it has not completed by seconds_till_timeout
        stdout, stderr = process.communicate(timeout=seconds_till_timeout)

        # Demonstrate the ability to log output directly from the subprocess
        LOG_LOCK.acquire()
        print(f"Output from {process_idx}: ({stdout}, {stderr})")
        LOG_LOCK.release()
        result = f"Process {process_idx}: completed successfully"
    except TimeoutExpired:
        # Catch any timeout error that comes from a terminated process
        result = f"Process {process_idx}: timed out"

    # Notify the shell that we have ended the current process
    LOG_LOCK.acquire()
    print(f"Ending process {process_idx}")
    LOG_LOCK.release()

    # Single return call that guarantees a result will be sent back to the
    # pool from this process
    return result


if __name__ == '__main__':
    main()
