import os
import json
import pytest
import datetime
import uuid
import random
from unittest.mock import patch, Mock
from pathlib import Path

from automates.program_analysis.Py2GrFN.py2grfn import python_file_to_grfn
import automates.model_assembly.networks 

DATA_DIR = "tests/data/program_analysis/py2grfn"
TEMP_DIR = "."

# TODO cleanup json files
def cleanup(filepath):
    os.remove(filepath)

def load_json_file(filepath):
    with open(filepath) as f:
        data = json.load(f)
    return data

def get_new_uuid_func():
    rd = random.Random()
    rd.seed(0)
    return lambda: uuid.UUID(int=rd.getrandbits(128)) 

############################################################################
#                                                                          #
#                            Python GrFN TEST                              #
#                                                                          #
############################################################################

@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_boolean_expr_and():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/boolean_expr/boolean_expr_and.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"
    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/boolean_expr/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({"y": False, "z": True})[0][0] == False

    # Cleanup
    cleanup(temp_json)

@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_boolean_expr_or():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/boolean_expr/boolean_expr_or.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"
    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/boolean_expr/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({"y": False, "z": True})[0][0] == True

    # Cleanup
    cleanup(temp_json)

@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_boolean_expr_not():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/boolean_expr/boolean_expr_not.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"
    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/boolean_expr/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == False

    # Cleanup
    cleanup(temp_json)

@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_boolean_expr_large():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/boolean_expr/boolean_expr_large.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/boolean_expr/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == True

    # Cleanup
    cleanup(temp_json)

@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_assignment_expr():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/assignment/assignment_expr.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/assignment/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == 12

    # Cleanup
    cleanup(temp_json)

@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_assignment_literal():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/assignment/assignment_literal.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/assignment/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == 10

    # Cleanup
    cleanup(temp_json)

@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_assignment_to_var():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/assignment/assignment_to_var.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/assignment/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == 20

    # Cleanup
    cleanup(temp_json)

@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_binary_operators_add():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/binary_operators/binary_operators_add.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/binary_operators/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == 30

    # Cleanup
    cleanup(temp_json)

@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_binary_operators_sub():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/binary_operators/binary_operators_sub.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/binary_operators/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == -10

    # Cleanup
    cleanup(temp_json)

@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_binary_operators_divide():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/binary_operators/binary_operators_divide.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/binary_operators/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == 2

    # Cleanup
    cleanup(temp_json)

@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_binary_operators_mul():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/binary_operators/binary_operators_mul.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/binary_operators/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == 200

    # Cleanup
    cleanup(temp_json)

@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_binary_operators_large():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/binary_operators/binary_operators_large.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/binary_operators/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == 60

    # Cleanup
    cleanup(temp_json)

@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_binary_operators_with_vars():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/binary_operators/binary_operators_with_vars.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/binary_operators/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == 60

    # Cleanup
    cleanup(temp_json)

@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_tuples_assign():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/tuples/tuples_assign.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/tuples/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    # TODO test once tuple execution is implemented
    # assert grfn({})[0] == 2

    # Cleanup
    cleanup(temp_json)


@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_tuples_return():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/tuples/tuples_return.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/tuples/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    # TODO test once tuple execution is implemented
    # assert grfn({})[0] == 2

    # Cleanup
    cleanup(temp_json)

@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_while_loops_basic():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/while_loops/while_loops_basic.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/while_loops/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    # TODO test once loop execution is implemented
    # assert grfn({})[0] == 2

    # Cleanup
    cleanup(temp_json)


@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_while_loops_large_expression():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/while_loops/while_loops_large_expression.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/while_loops/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    # TODO test once loop execution is implemented
    # assert grfn({})[0] == 2

    # Cleanup
    cleanup(temp_json)


@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_while_loops_nested():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/while_loops/while_loops_nested.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/while_loops/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    # TODO test once loop execution is implemented
    # assert grfn({})[0] == 2

    # Cleanup
    cleanup(temp_json)


@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_for_loops_basic():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/for_loops/for_loops_basic.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/for_loops/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    # TODO test once loop execution is implemented
    # assert grfn({})[0] == 2

    # Cleanup
    cleanup(temp_json)


@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_for_loops_nested():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/for_loops/for_loops_nested.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/for_loops/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    # TODO test once loop execution is implemented
    # assert grfn({})[0] == 2

    # Cleanup
    cleanup(temp_json)


@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_if_all_variable_def_types():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/if/if_all_variable_def_types.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/if/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == 2

    # Cleanup
    cleanup(temp_json)


@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_if_elif():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/if/if_elif.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/if/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == 2

    # Cleanup
    cleanup(temp_json)


@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_if_elif_else():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/if/if_elif_else.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/if/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == 2

    # Cleanup
    cleanup(temp_json)


@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_if_elif_else_large():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/if/if_elif_else_large.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/if/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == 2

    # Cleanup
    cleanup(temp_json)


@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_if_elif_large():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/if/if_elif_large.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/if/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == 2

    # Cleanup
    cleanup(temp_json)


@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_if_else():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/if/if_else.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/if/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == 2

    # Cleanup
    cleanup(temp_json)


@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_if_multiple_assigns_body():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/if/if_multiple_assigns_body.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/if/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({})[0] == 2

    # Cleanup
    cleanup(temp_json)


@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_if_multiple_variables_body():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/if/if_multiple_variables_body.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/if/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    res = grfn({})
    assert res[0] == 3
    assert res[1] == 2
    assert res[2] == 20

    # Cleanup
    cleanup(temp_json)


@patch.object(automates.model_assembly.networks, 'uuid', Mock(wraps=uuid))
@patch.object(automates.model_assembly.networks, 'datetime', Mock(wraps=datetime))
def test_nested_if():
    automates.model_assembly.networks.datetime.datetime.now.return_value = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    automates.model_assembly.networks.uuid.uuid4 = get_new_uuid_func()

    filepath = Path(f"{DATA_DIR}/if/nested_if.py")
    
    # Create grfn from python source
    grfn = python_file_to_grfn(filepath)

    # Generate json and assert it is the same as expected
    file_basename = os.path.basename(filepath).split(".py")[0]
    grfn.to_json_file(file_basename + ".json")

    temp_json = f"{TEMP_DIR}/{file_basename}.json"

    produced_json = load_json_file(Path(temp_json))
    expected_json = load_json_file(Path(f"{DATA_DIR}/if/{file_basename}.json"))
    assert sorted(produced_json.items()) == sorted(expected_json.items())

    # Assert running the grfn with some inputs produces the correct output
    assert grfn({}) == 2

    # Cleanup
    cleanup(temp_json)