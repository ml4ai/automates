from functools import reduce
import numpy as np

from .gromet import (
    BoxCall,
    Conditional,
    Expr,
    Expression,
    Function,
    Gromet,
    Box,
    Literal,
    RefFn,
    RefOp,
    UidPort,
)

# from pygraphviz import
class GrometExecutionException(Exception):
    pass


class GrometExecutionState:

    gromet: Gromet
    variable_map: dict
    port_map: dict
    wire_map: dict

    def __init__(self, gromet, variable_map, port_map, wire_map) -> None:
        self.gromet = gromet
        self.variable_map = variable_map
        self.port_map = port_map
        self.wire_map = wire_map

    def get_port_value(self, port_uid):
        return self.port_map[port_uid]

    def set_port_value(self, port_uid, val):
        self.port_map[port_uid] = val

    def is_port_initialized(self, port_uid):
        return port_uid in self.port_map and self.port_map[port_uid] != None

    def get_variable_value(self, v_uid):
        print(self.variable_map)
        return self.variable_map[v_uid]

    def set_variable_value(self, v_uid, val):
        self.variable_map[v_uid] = val

    def get_wire(self, wire_uid):
        return self.wire_map[wire_uid]

    @staticmethod
    def build_initial_from_gromet(gromet: Gromet):

        variable_map = dict()
        for v in gromet.variables:
            variable_map[v.uid] = np.array([None])

        port_map = dict()
        for p in gromet.ports:
            port_map[p.uid] = None

        wire_map = dict()
        for w in gromet.wires:
            wire_map[w.uid] = w

        return GrometExecutionState(gromet, variable_map, port_map, wire_map)


def execute_op(op: RefOp, values):
    result = None
    print(f"Values: {values}")

    def temp(a, b):
        print(f"Adding {a} + {b}")
        print(type(a))
        print(type(b))
        return a + b

    result = reduce(temp, values)
    if op.name == "Add":
        result = reduce(lambda a, b: a + b, values)
    elif op.name == "Sub":
        result = reduce(lambda a, b: a - b, values)
    elif op.name == "Mult":
        result = reduce(lambda a, b: a * b, values)
    elif op.name == "Div":
        result = reduce(lambda a, b: a / b, values)
    else:
        raise GrometExecutionException(f'Error: Unknown op "{op.name}"')

    return result


def execute_expr_tree(gromet: Gromet, expr: Expression, state: GrometExecutionState):
    arg_values = []
    for arg in expr.args:
        if isinstance(arg, Literal):
            arg_values.append(arg.value)
        elif isinstance(arg, str):
            arg_values.append(state.get_port_value(arg))
        elif isinstance(arg, Expr):
            arg_values.append(execute_expr_tree(gromet, arg, state))

    if isinstance(expr.call, RefOp):
        execute_op(expr.call, arg_values)
    # elif isinstance(tree.call, RefFn):
    # TODO should probably initialize sub box variable values then call?
    else:
        raise GrometExecutionException(
            f'Error: Unknwon tree call type "{type(expr.call)}"'
        )


def execute_expression_box(
    gromet: Gromet, expr: Expression, state: GrometExecutionState
):

    tree = expr.tree
    return execute_expr_tree(gromet, tree, state)


def is_expr_executable(tree: Expr, state: GrometExecutionState):
    return all(
        [
            isinstance(arg, Literal)
            or (isinstance(arg, Expr) and (is_expr_executable(arg, state)))
            or (isinstance(arg, str) and state.is_port_initialized(arg))
            for arg in tree.args
        ]
    )


def execute_function_box(
    gromet: Gromet, root_box: Function, state: GrometExecutionState
):

    box_queue = [
        [box for box in gromet.boxes if box_uid == box.uid][0]
        for box_uid in root_box.boxes
    ]

    while len(box_queue) > 0:
        box = box_queue[0]
        del box_queue[0]

        if isinstance(box, BoxCall):
            called_box_match = [box for box in gromet.boxes if box.uid == box.call]
            if len(called_box_match) == 0:
                raise GrometExecutionException(
                    f'Error: Unable to find called box "{box.call}".'
                )
            execute_function_box(gromet, called_box_match[0], state)
        elif isinstance(box, Expression):
            tree = box.tree

            # port_map = {
            #     port_uid: [port for port in gromet.ports if port_uid == port.uid][0]
            #     for port_uid in box.ports
            # }

            if not is_expr_executable(tree, state):
                box_queue.append(box)
                continue

            res = execute_expression_box(gromet, box, state)
            print(res)

            expression_output_ports = [
                port
                for port_uid in box.ports
                for port in [
                    port
                    for port in gromet.ports
                    if port.uid == port_uid and port.type == "output"
                ]
            ]

            for port in expression_output_ports:
                for wire in gromet.wires:
                    if wire.src == port.uid:
                        state.set_port_value(
                            port.uid,
                        )
            print(box)
            print("Outputs")
            print(len(expression_output_ports))
            print(expression_output_ports)

        elif isinstance(box, Conditional):
            return

        elif isinstance(box, Function):
            return

        else:
            raise GrometExecutionException(
                f'Error: Unknown GroMEt box type "{type(box)}"'
            )


def execute_gromet(gromet: Gromet, input_port_map: dict):
    """
    Initialize the execution of the GroMEt object.

    Args:
        gromet (Gromet): GroMEt to execute.
        input_map (dict): A map of GroMEt UIDs to initial values.

    Returns:
        Dict: Results map for output variables.
    """
    state = GrometExecutionState.build_initial_from_gromet(gromet)

    # TODO vectorized inputs longer than 1
    # for v in gromet.variables:
    #     if v.uid in input_map:
    #         state.set_variable_value(v.uid, np.array(input_map[v.uid]))

    # This root box needs to be a function box
    root_box = [box for box in gromet.boxes if box.uid == gromet.root][0]

    root_port_objects = [
        [port for port in gromet.ports if port.uid == port_uid][0]
        for port_uid in root_box.ports
    ]
    input_root_ports = [port for port in root_port_objects if port.type == "input"]

    # TODO vectorized inputs longer than 1
    for root_uid, val in input_port_map.items():
        for wire_uid in root_box.wires:
            wire = state.get_wire(wire_uid)
            if wire.src == root_uid:
                state.set_port_value(wire.src, np.array(val))

    from pprint import pprint

    print("=========================")
    # print(f"Root input ports {input_root_ports}")
    print(f"Root input ports")
    pprint(state.port_map)
    print("=========================")

    return execute_function_box(gromet, root_box, state)
