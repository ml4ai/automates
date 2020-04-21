from pathlib import Path
from typing import Dict, Iterable, Set, Union
from typing import List
import importlib
import datetime
import inspect
import uuid
import json
import os
import re

import networkx as nx
from pygraphviz import AGraph
from networkx.algorithms.simple_paths import all_simple_paths

# from model_analysis.analysis import get_max_s2_sensitivity
from model_analysis.utils import ScopeNode, choose_font
from program_analysis.for2py import f2grfn
import numpy as np

FONT = choose_font()

dodgerblue3 = "#1874CD"
forestgreen = "#228b22"


class ComputationalGraph(nx.DiGraph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.FCG = self.to_FCG()
        self.function_sets = self.build_function_sets()

    def get_input_nodes(self) -> List[str]:
        """ Get all input nodes from a network. """
        return [n for n, d in self.in_degree() if d == 0]

    def get_output_nodes(self) -> List[str]:
        """ Get all output nodes from a network. """
        return [n for n, d in self.out_degree() if d == 0]

    def to_FCG(self):
        G = nx.DiGraph()
        for (name, attrs) in self.nodes(data=True):
            if attrs["type"] == "function":
                for predecessor_variable in self.predecessors(name):
                    for predecessor_function in self.predecessors(
                        predecessor_variable
                    ):
                        G.add_edge(predecessor_function, name)
        return G

    def build_function_sets(self):
        initial_funcs = [n for n, d in self.FCG.in_degree() if d == 0]
        distances = dict()

        def find_distances(funcs, dist):
            all_successors = list()
            for func in funcs:
                distances[func] = dist
                all_successors.extend(self.FCG.successors(func))
            if len(all_successors) > 0:
                find_distances(list(set(all_successors)), dist + 1)

        find_distances(initial_funcs, 0)
        call_sets = dict()
        for func_name, call_dist in distances.items():
            if call_dist in call_sets:
                call_sets[call_dist].add(func_name)
            else:
                call_sets[call_dist] = {func_name}

        function_set_dists = sorted(
            call_sets.items(), key=lambda t: (t[0], len(t[1]))
        )
        function_sets = [func_set for _, func_set in function_set_dists]
        return function_sets

    def run(
        self, inputs: Dict[str, Union[float, Iterable]],
    ) -> Union[float, Iterable]:
        """Executes the GrFN over a particular set of inputs and returns the
        result.

        Args:
            inputs: Input set where keys are the names of input nodes in the
                GrFN and each key points to a set of input values (or just one).

        Returns:
            A set of outputs from executing the GrFN, one for every set of
            inputs.
        """
        full_inputs = {self.input_name_map[n]: v for n, v in inputs.items()}
        # Set input values
        for i in self.inputs:
            value = full_inputs[i]
            if isinstance(value, float):
                value = np.array([value], dtype=np.float32)
            if isinstance(value, int):
                value = np.array([value], dtype=np.int32)
            elif isinstance(value, list):
                value = np.array(value, dtype=np.float32)

            self.nodes[i]["value"] = value
        for func_set in self.function_sets:
            for func_name in func_set:
                lambda_fn = self.nodes[func_name]["lambda_fn"]
                output_node = list(self.successors(func_name))[0]

                signature = self.nodes[func_name]["func_inputs"]
                input_values = [self.nodes[n]["value"] for n in signature]
                res = lambda_fn(*input_values)

                # Convert output to a NumPy matrix if a constant was returned
                if len(input_values) == 0:
                    res = np.array(res, dtype=np.float32)

                self.nodes[output_node]["value"] = res

        # Return the output
        return [self.nodes[o]["value"] for o in self.outputs]

    def to_CAG(self):
        """ Export to a Causal Analysis Graph (CAG) PyGraphviz AGraph object.
        The CAG shows the influence relationships between the variables and
        elides the function nodes."""

        G = nx.DiGraph()
        for (name, attrs) in self.nodes(data=True):
            if attrs["type"] == "variable":
                cag_name = attrs["cag_label"]
                G.add_node(cag_name, **attrs)
                for pred_fn in self.predecessors(name):
                    for pred_var in self.predecessors(pred_fn):
                        v_attrs = self.nodes[pred_var]
                        v_name = v_attrs["cag_label"]
                        G.add_node(v_name, **self.nodes[pred_var])
                        G.add_edge(v_name, cag_name)

        return G

    def CAG_to_AGraph(self):
        """Returns a variable-only view of the GrFN in the form of an AGraph.

        Returns:
            type: A CAG constructed via variable influence in the GrFN object.

        """
        CAG = self.to_CAG()
        for name, data in CAG.nodes(data=True):
            CAG.nodes[name]["label"] = data["cag_label"]
        A = nx.nx_agraph.to_agraph(CAG)
        A.graph_attr.update(
            {"dpi": 227, "fontsize": 20, "fontname": "Menlo", "rankdir": "TB"}
        )
        A.node_attr.update(
            {
                "shape": "rectangle",
                "color": "#650021",
                "style": "rounded",
                "fontname": "Menlo",
            }
        )
        A.edge_attr.update({"color": "#650021", "arrowsize": 0.5})
        return A

    def FCG_to_AGraph(self):
        """ Build a PyGraphviz AGraph object corresponding to a call graph of
        functions. """

        A = nx.nx_agraph.to_agraph(self.FCG)
        A.graph_attr.update(
            {"dpi": 227, "fontsize": 20, "fontname": "Menlo", "rankdir": "TB"}
        )
        A.node_attr.update(
            {"shape": "rectangle", "color": "#650021", "style": "rounded"}
        )
        A.edge_attr.update({"color": "#650021", "arrowsize": 0.5})
        return A


class GroundedFunctionNetwork(ComputationalGraph):
    """
    Representation of a GrFN model as a DiGraph with a set of input nodes and
    currently a single output. The DiGraph is composed of variable nodes and
    function nodes. Function nodes store an actual Python function with the
    expected set of ordered input arguments that correspond to the variable
    inputs of that node. Variable nodes store a value. This value can be any
    data type found in Python. When no value exists for a variable the value
    key will be set to None. Importantly only function nodes can be children or
    parents of variable nodes, and the reverse is also true. Both variable and
    function nodes can be inputs, but the output will always be a variable
    node.
    """

    def __init__(self, G, scope_tree, outputs):
        super().__init__(G)
        self.outputs = outputs
        self.inputs = [
            n
            for n, d in self.in_degree()
            if d == 0 and self.nodes[n]["type"] == "variable"
        ]
        self.input_name_map = {
            self.nodes[n]["basename"]: n for n in self.inputs
        }

        self.node_name_map = {
            d["label"]: l
            for l, d in self.nodes(data=True)
            if d["type"] == "variable"
        }
        # self.outputs = outputs
        self.subgraphs = scope_tree

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "\n".join(self.traverse_nodes(self.inputs))

    def traverse_nodes(self, node_set, depth=0):
        """BFS traversal of nodes that returns name traversal as large string.

        Args:
            node_set: Set of input nodes to begin traversal.
            depth: Current traversal depth for child node viewing.

        Returns:
            type: String containing tabbed traversal view.
        """

        tab = "  "
        result = list()
        for n in node_set:
            repr = (
                n
                if self.nodes[n]["type"] == "variable"
                else f"{n}{inspect.signature(self.nodes[n]['lambda_fn'])}"
            )

            result.append(f"{tab * depth}{repr}")
            result.extend(
                self.traverse_nodes(self.successors(n), depth=depth + 1)
            )
        return result

    @classmethod
    def from_json_file(cls, filepath: str):
        # Load the JSON data file
        grfn_json = json.load(open(filepath))
        G = nx.DiGraph()

        # Add edges data from JSON
        for func_connection in grfn_json["edges"]:
            func_node = func_connection["function"]
            for src_node in func_connection["in"]:
                G.add_edge(src_node, func_node)
            for dst_node in func_connection["out"]:
                G.add_edge(func_node, dst_node)

        # Access the variable and function node lists
        variables = {v["uid"]: v for v in grfn_json["variables"]}
        functions = {f["uid"]: f for f in grfn_json["functions"]}
        relations = {
            e["function"]: (e["in"], e["out"]) for e in grfn_json["edges"]
        }

        S = nx.DiGraph()
        for container in grfn_json["containers"]:
            con_name = container["name"]
            parent_name = container["parent"]
            all_vertices = container["vertices"]
            container_color = (
                "navyblue" if container["exit"] is not None else "forestgreen"
            )
            S.add_node(
                con_name,
                parent=parent_name,
                exit_node=container["exit"],
                func_node_list=[f for f in functions if f in all_vertices],
                vertex_list=all_vertices,
            )

            if parent_name is not None:
                S.add_edge(parent_name, con_name)

            for vert_id in container["vertices"]:
                if vert_id in variables:
                    var_node = variables[vert_id]
                    var_name = var_node["name"]
                    (basename, index) = var_name.split("::")
                    is_exit = basename == "EXIT"
                    G.add_node(
                        var_node["uid"],
                        ref_id=var_node["reference"],
                        var_data_name=var_node["data-type"]["name"],
                        var_data_type=var_node["data-type"]["type"],
                        type="variable",
                        color="crimson",
                        fontcolor="white" if is_exit else "black",
                        fillcolor="crimson" if is_exit else "white",
                        style="filled" if is_exit else "",
                        parent=con_name,
                        label=f"{basename}\n({index})",
                        cag_label=f"{basename}",
                        basename=basename,
                        padding=15,
                        value=None,
                    )
                elif vert_id in functions:
                    func_node = functions[vert_id]

                    # Build the name of the function to be executed
                    func_id = func_node["uid"]
                    func_type = func_node["type"]
                    lambda_name = func_type + "_" + re.sub(r"-", "_", func_id)

                    # Build the argument list for the function
                    lambda_str = func_node["lambda"]
                    all_var_mentions = re.findall(r"x[0-9]+\b", lambda_str)
                    input_var_list = sorted(list(set(all_var_mentions)))

                    # Build and execute the function then retrieve the func ref
                    func_str = f"def {lambda_name}({', '.join(input_var_list)}): return {lambda_str}"
                    exec(func_str)
                    func_ref = locals()[lambda_name]

                    G.add_node(
                        func_id,
                        type="function",
                        func_type=func_type,
                        lambda_fn=func_ref,
                        func_inputs=relations[vert_id][0],
                        visited=False,
                        shape="rectangle",
                        parent=con_name,
                        label=func_type[0].upper(),
                        padding=10,
                    )
                else:
                    raise ValueError(f"Unmatched vertex ID in {con_name}")
        outputs = [
            n
            for n, d in G.in_degree()
            if d == 0 and G.nodes[n]["type"] == "variable"
        ]
        return cls(G, S, outputs)

    @classmethod
    def from_json_and_lambdas(cls, file: str, lambdas):
        """Builds a GrFN from a JSON object.

        Args:
            cls: The class variable for object creation.
            file: Filename of a GrFN JSON file.
            lambdas: A lambdas module

        Returns:
            type: A GroundedFunctionNetwork object.

        """
        with open(file, "r") as f:
            data = json.load(f)

        return cls.from_dict(data, lambdas)

    @classmethod
    def from_dict(cls, data: Dict, lambdas_path):
        """Builds a GrFN object from a set of extracted function data objects
        and an associated file of lambda functions.

        Args:
            cls: The class variable for object creation.
            data: A set of function data object that specify the wiring of a
                  GrFN object.
            lambdas_path: Path to a lambdas file containing functions to be
                computed during GrFN execution.

        Returns:
            A GroundedFunctionNetwork object.

        """
        lambdas = importlib.__import__(str(Path(lambdas_path).stem))
        functions = {d["name"]: d for d in data["containers"]}
        variables = {v["name"]: v for v in data["variables"]}
        varname2id = {name: str(uuid.uuid4()) for name in variables.keys()}
        occurrences = {}
        G = nx.DiGraph()
        scope_tree = nx.DiGraph()

        def identity(x):
            return x

        def get_variable_reference(parent: str, basename: str, index: str):
            (namespace, context, container, _) = parent.split("::")
            if context != "@global":
                container = f"{context}.{container}"
            return f"@variable::{namespace}::{container}::{basename}::{index}"

        def add_variable_node(
            parent: str, basename: str, index: str, is_exit: bool = False
        ):
            var_identifier = varname2id[
                get_variable_reference(parent, basename, index)
            ]
            G.add_node(
                var_identifier,
                type="variable",
                color="crimson",
                fontcolor="white" if is_exit else "black",
                fillcolor="crimson" if is_exit else "white",
                style="filled" if is_exit else "",
                parent=parent,
                basename=basename,
                index=index,
                label=f"{basename}\n({index})",
                cag_label=f"{basename}",
                padding=15,
                value=None,
            )
            return var_identifier

        def process_wiring_statement(stmt, scope, inputs, cname):
            lambda_name = stmt["function"]["name"]
            lambda_identifier = str(uuid.uuid4())

            stmt_type = lambda_name.split("__")[-3]
            if stmt_type == "assign" and len(stmt["input"]) == 0:
                stmt_type = "literal"

            for output in stmt["output"]:
                (_, var_name, idx) = output.split("::")
                node_name = add_variable_node(
                    scope.name, var_name, idx, is_exit=var_name == "EXIT"
                )
                G.add_edge(lambda_identifier, node_name)

            ordered_inputs = list()
            for inp in stmt["input"]:
                if inp.endswith("-1"):
                    (parent, var_name, idx) = inputs[inp]
                else:
                    parent = scope.name
                    (_, var_name, idx) = inp.split("::")

                node_name = add_variable_node(parent, var_name, idx)
                ordered_inputs.append(node_name)
                G.add_edge(node_name, lambda_identifier)

            G.add_node(
                lambda_identifier,
                type="function",
                func_type=stmt_type,
                lambda_fn=getattr(lambdas, lambda_name),
                func_inputs=ordered_inputs,
                visited=False,
                shape="rectangle",
                parent=scope.name,
                label=stmt_type[0].upper(),
                padding=10,
            )

        def process_call_statement(stmt, scope, inputs, cname):
            container_name = stmt["function"]["name"]
            if container_name not in occurrences:
                occurrences[container_name] = 0

            new_container = functions[container_name]
            container_color = (
                "navyblue" if new_container["repeat"] else "forestgreen"
            )
            new_scope = ScopeNode(
                new_container, occurrences[container_name], parent=scope
            )
            scope_tree.add_node(new_scope.name, color=container_color)
            scope_tree.add_edge(scope.name, new_scope.name)

            input_values = list()
            for inp in stmt["input"]:
                if inp.endswith("-1"):
                    (parent, var_name, idx) = inputs[inp]
                else:
                    parent = scope.name
                    (_, var_name, idx) = inp.split("::")
                input_values.append((parent, var_name, idx))

            callee_ret, callee_up = process_container(
                new_scope, input_values, container_name
            )

            caller_ret, caller_up = list(), list()
            for var in stmt["output"]:
                parent = scope.name
                (_, var_name, idx) = var.split("::")
                node_name = add_variable_node(parent, var_name, idx)
                caller_ret.append(node_name)

            for var in stmt["updated"]:
                parent = scope.name
                (_, var_name, idx) = var.split("::")
                node_name = add_variable_node(parent, var_name, idx)
                caller_up.append(node_name)

            for callee_var, caller_var in zip(callee_ret, caller_ret):
                lambda_identifier = str(uuid.uuid4())
                G.add_node(
                    lambda_identifier,
                    type="function",
                    func_type="assign",
                    lambda_fn=identity,
                    func_inputs=[callee_var],
                    shape="rectangle",
                    parent=scope.name,
                    label="A",
                    padding=10,
                )
                G.add_edge(callee_var, lambda_identifier)
                G.add_edge(lambda_identifier, caller_var)

            for callee_var, caller_var in zip(callee_up, caller_up):
                lambda_identifier = str(uuid.uuid4())
                G.add_node(
                    lambda_identifier,
                    type="function",
                    func_type="assign",
                    lambda_fn=identity,
                    func_inputs=[callee_var],
                    shape="rectangle",
                    parent=scope.name,
                    label="A",
                    padding=10,
                )
                G.add_edge(callee_var, lambda_identifier)
                G.add_edge(lambda_identifier, caller_var)
            occurrences[container_name] += 1

        def process_container(scope, input_vals, cname):
            if len(scope.arguments) == len(input_vals):
                input_vars = {
                    a: v for a, v in zip(scope.arguments, input_vals)
                }
            elif len(scope.arguments) > 0:
                input_vars = {
                    a: (scope.name,) + tuple(a.split("::")[1:])
                    for a in scope.arguments
                }

            for stmt in scope.body:
                func_def = stmt["function"]
                func_type = func_def["type"]
                if func_type == "lambda":
                    process_wiring_statement(stmt, scope, input_vars, cname)
                elif func_type == "container":
                    process_call_statement(stmt, scope, input_vars, cname)
                else:
                    raise ValueError(f"Undefined function type: {func_type}")

            return_list, updated_list = list(), list()
            for var_name in scope.returns:
                (_, basename, idx) = var_name.split("::")
                return_list.append(
                    varname2id[
                        get_variable_reference(scope.name, basename, idx)
                    ]
                )

            for var_name in scope.updated:
                (_, basename, idx) = var_name.split("::")
                updated_list.append(
                    varname2id[
                        get_variable_reference(scope.name, basename, idx)
                    ]
                )
            return return_list, updated_list

        root = data["start"][0]
        occurrences[root] = 0
        cur_scope = ScopeNode(functions[root], occurrences[root])
        scope_tree.add_node(cur_scope.name, color="forestgreen")
        returns, updates = process_container(cur_scope, [], root)
        return cls(G, scope_tree, returns + updates)

    @classmethod
    def from_python_file(
        cls, python_file, lambdas_path, json_filename: str, stem: str
    ):
        """Builds GrFN object from Python file."""
        with open(python_file, "r") as f:
            pySrc = f.read()
        return cls.from_python_src(pySrc, lambdas_path, json_filename, stem)

    @classmethod
    def from_python_src(
        cls,
        pySrc,
        python_file: str,
        fortran_file: str,
        module_log_file_path: str,
        mod_mapper_dict: list,
        processing_modules: bool,
    ):
        lambdas_path = python_file.replace(".py", "_lambdas.py")
        # Builds GrFN object from Python source code.
        pgm_dict = f2grfn.generate_grfn(
            pySrc,
            python_file,
            lambdas_path,
            mod_mapper_dict,
            fortran_file,
            module_log_file_path,
            processing_modules,
        )

        G = cls.from_dict(pgm_dict, lambdas_path)

        # Cleanup intermediate files.
        variable_map_filename = python_file.replace(".py", "_variable_map.pkl")
        os.remove(variable_map_filename)
        rectified_xml_filename = "rectified_" + str(Path(python_file)).replace(
            ".py", ".xml"
        )
        os.remove(rectified_xml_filename)
        return G

    @classmethod
    def from_fortran_file(cls, fortran_file: str, tmpdir: str = "."):
        """Builds GrFN object from a Fortran program."""

        root_dir = os.path.abspath(tmpdir)

        (
            python_sources,
            translated_python_files,
            mod_mapper_dict,
            fortran_filename,
            module_log_file_path,
            processing_modules,
        ) = f2grfn.fortran_to_grfn(
            fortran_file,
            temp_dir=str(tmpdir),
            root_dir_path=root_dir,
            processing_modules=False,
        )

        # For now, just taking the first translated file.
        # TODO - generalize this.
        python_file = translated_python_files[0]
        G = cls.from_python_src(
            python_sources[0][0],
            python_file,
            fortran_file,
            module_log_file_path,
            mod_mapper_dict,
            processing_modules,
        )

        return G

    @classmethod
    def from_fortran_src(cls, fortran_src: str, dir: str = "."):
        """ Create a GroundedFunctionNetwork instance from a string with raw
        Fortran code.

        Args:
            fortran_src: A string with Fortran source code.
            dir: (Optional) - the directory in which the temporary Fortran file
                will be created (make sure you have write permission!) Defaults to
                the current directory.
        Returns:
            A GroundedFunctionNetwork instance
        """
        import tempfile

        fp = tempfile.NamedTemporaryFile("w+t", delete=False, dir=dir)
        fp.writelines(fortran_src)
        fp.close()
        G = cls.from_fortran_file(fp.name, dir)
        os.remove(fp.name)
        return G

    def to_json(self):
        """Experimental outputting a GrFN to a JSON file."""

        def func_type_from_name(func_name):
            (_, _, _, _, full_func_name) = func_name.split("::")
            (_, _, func_type, _, _) = full_func_name.split("__")
            return func_type

        def get_function_source(lambda_ref):
            (source_list, _) = inspect.getsourcelines(lambda_ref)
            arg_str = re.findall(r"\(.*\)", source_list[0])[0]
            args_and_types = [
                s for s in re.findall(r"\w*", arg_str) if s != ""
            ]
            args = [s for i, s in enumerate(args_and_types) if i % 2 == 0]
            source_lines = list()
            for i, line in enumerate(source_list[1:]):
                for j, arg in enumerate(args):
                    line = re.sub(rf"\b{arg}\b", f"x{j}", line)
                if i + 1 == len(source_list) - 1:
                    line = line.replace("return ", "")
                source_lines.append(line.strip())
            lambda_code = ";".join(source_lines)
            return lambda_code

        def variable_type_data(var_basename):
            # NOTE: This is not yet generalized, need to improve that soon
            if var_basename.startswith("IF_"):
                return {
                    "name": "boolean",
                    "type": "binary",
                    "domain": [True, False],
                }
            elif var_basename == "doy":
                return {
                    "name": "int32",
                    "type": "discrete",
                    "domain": [(-2147483647, 2147483647)],
                }
            elif var_basename == "meevp":
                return {
                    "name": "string",
                    "type": "ordinal",
                    "domain": ["A", "W"],
                }
            else:
                return {
                    "name": "float32",
                    "type": "continuous",
                    "domain": [(-3.40282347e38, 3.40282347e38)],
                }

        containers = {
            name: {
                "name": name,
                "parent": None,
                "exit": None,
                "vertices": list(),
            }
            for name in self.subgraphs.nodes
        }

        variables, functions, edges = list(), list(), list()
        for identifier, data in self.nodes(data=True):
            containers[data["parent"]]["vertices"].append(identifier)
            if data["type"] == "variable":
                basename = data["basename"]
                idx = data["index"]
                variables.append(
                    {
                        "name": f"{basename}::{idx}",
                        "uid": identifier,
                        "reference": None,
                        "data-type": variable_type_data(basename),
                    }
                )
            elif data["type"] == "function":
                functions.append(
                    {
                        "type": data["func_type"],
                        "uid": identifier,
                        "reference": None,
                        "lambda": get_function_source(data["lambda_fn"]),
                    }
                )

                func_inputs = data["func_inputs"]
                func_outputs = list(self.successors(identifier))
                edges.append(
                    {
                        "in": func_inputs,
                        "function": identifier,
                        "out": func_outputs,
                    }
                )
            else:
                raise ValueError(f"Unrecognized node type: {data['type']}")

        return {
            "uid": str(uuid.uuid4()),
            "data_created": datetime.datetime.now().strftime("%Y-%m-%d"),
            "edges": edges,
            "functions": functions,
            "variables": variables,
            "containers": list(containers.values()),
        }

    def to_json_file(self, filename):
        GrFN_json = self.to_json()
        json.dump(GrFN_json, open(filename, "w"))

    def get_GrFN_edges(self):
        return [
            (self.nodes[src_id]["label"], self.nodes[dst_id]["label"])
            for src_id, dst_id in self.edges()
        ]

    def to_AGraph(self):
        """ Export to a PyGraphviz AGraph object. """
        A = nx.nx_agraph.to_agraph(self)

        node_names = [
            n for n, d in self.nodes(data=True) if d["type"] == "variable"
        ]
        input_nodes = set(
            [n for n in node_names if len(list(self.predecessors(n))) == 0]
        )
        output_nodes = set(
            [n for n in node_names if len(list(self.successors(n))) == 0]
        )
        A.graph_attr.update(
            {"dpi": 227, "fontsize": 20, "fontname": "Menlo", "rankdir": "TB"}
        )

        A.node_attr.update({"fontname": "Menlo"})

        def build_tree(cluster_name, node_attrs, root_graph):
            subgraph_nodes = [
                node_name
                for node_name, node_data in self.nodes(data=True)
                if node_data["parent"] == cluster_name
            ]
            # root_graph.add_nodes_from(subgraph_nodes)
            subgraph = root_graph.add_subgraph(
                subgraph_nodes,
                name=f"cluster_{cluster_name}",
                label=cluster_name,
                style="bold, rounded",
                rankdir="TB",
                color=node_attrs[cluster_name]["color"],
            )

            subgraph.add_subgraph(input_nodes, rank="same")
            subgraph.add_subgraph(output_nodes, rank="same")
            function_sets = self.build_function_sets()
            for func_set in function_sets:
                subgraph.add_subgraph(list(func_set), rank="same")
                output_var_nodes = list()
                for func_node in func_set:
                    succs = list(self.successors(func_node))
                    output_var_nodes.extend(succs)
                output_var_nodes = list(set(output_var_nodes) - output_nodes)
                subgraph.add_subgraph(output_var_nodes, rank="same")

            for n in self.subgraphs.successors(cluster_name):
                build_tree(n, node_attrs, subgraph)

        root = [n for n, d in self.subgraphs.in_degree() if d == 0][0]
        node_data = {n: d for n, d in self.subgraphs.nodes(data=True)}
        build_tree(root, node_data, A)

        return A


class ForwardInfluenceBlanket(ComputationalGraph):
    """
    This class takes a network and a list of a shared nodes between the input
    network and a secondary network. From this list a shared nodes and blanket
    network is created including all of the nodes between any input/output pair
    in the shared nodes, as well as all nodes required to blanket the network
    for forward influence. This class itself becomes the blanket and inherits
    from the ComputationalGraph class.
    """

    def __init__(self, G: GroundedFunctionNetwork, shared_nodes: Set[str]):
        # super().__init__()
        outputs = G.outputs
        inputs = set(G.inputs).intersection(shared_nodes)

        # Get all paths from shared inputs to shared outputs
        path_inputs = shared_nodes - set(outputs)
        io_pairs = [(inp, outputs[0]) for inp in path_inputs]
        paths = [p for (i, o) in io_pairs for p in all_simple_paths(G, i, o)]

        # Get all edges needed to blanket the included nodes
        main_nodes = {node for path in paths for node in path}
        main_edges = {
            (n1, n2) for path in paths for n1, n2 in zip(path, path[1:])
        }
        self.blanket_nodes = set()
        add_nodes, add_edges = list(), list()

        def place_var_node(var_node):
            prev_funcs = list(G.predecessors(var_node))
            if len(prev_funcs) > 0 and G.nodes[prev_funcs[0]]["label"] == "L":
                prev_func = prev_funcs[0]
                add_nodes.extend([var_node, prev_func])
                add_edges.append((prev_func, var_node))
            else:
                self.blanket_nodes.add(var_node)

        for node in main_nodes:
            if G.nodes[node]["type"] == "function":
                for var_node in G.predecessors(node):
                    if var_node not in main_nodes:
                        add_edges.append((var_node, node))
                        if "::IF_" in var_node:
                            if_func = list(G.predecessors(var_node))[0]
                            add_nodes.extend([if_func, var_node])
                            add_edges.append((if_func, var_node))
                            for new_var_node in G.predecessors(if_func):
                                add_edges.append((new_var_node, if_func))
                                place_var_node(new_var_node)
                        else:
                            place_var_node(var_node)

        main_nodes |= set(add_nodes)
        main_edges |= set(add_edges)
        main_nodes = main_nodes - inputs - set(outputs)

        orig_nodes = G.nodes(data=True)

        F = nx.DiGraph()

        F.add_nodes_from([(n, d) for n, d in orig_nodes if n in inputs])
        for node in inputs:
            F.nodes[node]["color"] = dodgerblue3
            F.nodes[node]["fontcolor"] = dodgerblue3
            F.nodes[node]["penwidth"] = 3.0
            F.nodes[node]["fontname"] = FONT

        F.add_nodes_from(
            [(n, d) for n, d in orig_nodes if n in self.blanket_nodes]
        )
        for node in self.blanket_nodes:
            F.nodes[node]["fontname"] = FONT
            F.nodes[node]["color"] = forestgreen
            F.nodes[node]["fontcolor"] = forestgreen

        F.add_nodes_from([(n, d) for n, d in orig_nodes if n in main_nodes])
        for node in main_nodes:
            F.nodes[node]["fontname"] = FONT

        for out_var_node in outputs:
            F.add_node(out_var_node, **G.nodes[out_var_node])
            F.nodes[out_var_node]["color"] = dodgerblue3
            F.nodes[out_var_node]["fontcolor"] = dodgerblue3

        F.add_edges_from(main_edges)
        super().__init__(F)

        # self.FCG = self.to_FCG()
        # self.function_sets = self.build_function_sets()

    @classmethod
    def from_GrFN(cls, G1, G2):
        """ Creates a ForwardInfluenceBlanket object representing the
        intersection of this model with the other input model.

        Args:
            G1: The GrFN model to use as the basis for this FIB
            G2: The GroundedFunctionNetwork object to compare this model to.

        Returns:
            A ForwardInfluenceBlanket object to use for model comparison.
        """

        if not (
            isinstance(G1, GroundedFunctionNetwork)
            and isinstance(G2, GroundedFunctionNetwork)
        ):
            raise TypeError(
                f"Expected two GrFNs, but got ({type(G1)}, {type(G2)})"
            )

        g1_var_nodes = {
            d["basename"]
            for (n, d) in G1.nodes(data=True)
            if d["type"] == "variable"
        }
        g2_var_nodes = {
            d["basename"]
            for (n, d) in G2.nodes(data=True)
            if d["type"] == "variable"
        }

        shared_vars = list(g1_var_nodes.intersection(g2_var_nodes))
        orig_shared_vars = [
            d["label"]
            for n, d in G1.nodes(data=True)
            if d["type"] == "variable" and d["basename"] in shared_vars
        ]

        shared_var_ids = {G1.node_name_map[name] for name in orig_shared_vars}

        return cls(G1, shared_var_ids)

    def run(
        self,
        inputs: Dict[str, Union[float, Iterable]],
        covers: Dict[str, Union[float, Iterable]],
    ) -> Union[float, Iterable]:
        """Executes the FIB over a particular set of inputs and returns the
        result.
        Args:
            inputs: Input set where keys are the names of input nodes in the
              GrFN and each key points to a set of input values (or just one).
        Returns:
            A set of outputs from executing the GrFN, one for every set of
            inputs.
        """
        # Abort run if covers does not match our expected cover set
        if len(covers) != len(self.blanket_nodes):
            raise ValueError("Incorrect number of cover values.")

        # Set the cover node values
        for node_name, val in covers.items():
            self.nodes[node_name]["value"] = val

        return super().run(inputs)

    def to_AGraph(self):
        A = nx.nx_agraph.to_AGraph(self)
        A.graph_attr.update({"dpi": 227, "fontsize": 20})
        A.node_attr.update({"shape": "rectangle", "style": "rounded"})
        A.edge_attr.update({"arrowsize": 0.5})
        return A
