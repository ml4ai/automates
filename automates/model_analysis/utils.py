import time
import functools
import platform
from typing import Iterable


def timeit(func):
    """Record the runtime of the decorated function."""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        return (value, end_time - start_time)

    return wrapper_timer


def choose_font():
    operating_system = platform.system()

    if operating_system == "Darwin":
        font = "Gill Sans"
    elif operating_system == "Windows":
        font = "Candara"
    else:
        font = "Ubuntu"

    return font


def results_to_csv(
    filepath: str, inputMat: Iterable, outputMat: Iterable
) -> None:
    # TODO khan: implement this such that each row of a csv file has a set of
    # inputs followed by a set of outputs
    return NotImplemented


def results_to_json(
    filepath: str, inputMat: Iterable, outputMat: Iterable
) -> None:
    # TODO khan: implement this such that each row of a json file as an object
    # with the keys (input_data, output_data). Store the corresponding arrays as
    # lists at those outputs
    return NotImplemented


def bounds_from_csv(filepath: str) -> dict:
    # TODO khan: Implement bound loading from a CSV file here
    return NotImplemented


def bounds_from_json(filepath: str) -> dict:
    # TODO khan: Implement bound loading from a JSON file here
    return NotImplemented
