from numbers import Number
from copy import deepcopy
from uuid import uuid4
from pprint import pprint
import functools
import operator

import json
import inspect
import re

import SALib as SAL
from SALib.sample import saltelli, latin
from SALib.analyze import sobol, fast, rbd_fast
import numpy as np
import networkx as nx
from tqdm import tqdm

from automates.model_assembly.networks import GroundedFunctionNetwork
from .utils import timeit


class SensitivityAnalysisInputError(Exception):
    pass


class SensitivityAnalysisExecutionError(Exception):
    pass


class SensitivityIndices(object):
    """This class creates an object with first and second order sensitivity
    indices as well as the total sensitivty index for a given sample size. It
    also contains the confidence interval associated with the computation of
    each index. The indices are in the form of a dictionary and they can be saved
    to or read from JSON, pickle, and csv files. In addition, the maximum and
    minimum second order of the indices between any two input variables can be
    determined using the max (min) and argmax (argmin) methods.
    """

    def __init__(self, S: dict, problem: dict):
        """
        Args:
            S: A SALib dictionary from analysis
        """
        self.parameter_list = problem["names"]
        self.O1_indices = np.array(S["S1"]) if "S1" in S else None
        self.O2_indices = np.array(S["S2"]) if "S2" in S else None
        self.OT_indices = np.array(S["ST"]) if "ST" in S else None
        self.O1_confidence = np.array(S["S1_conf"]) if "S1_conf" in S else None
        self.O2_confidence = np.array(S["S2_conf"]) if "S2_conf" in S else None
        self.OT_confidence = np.array(S["ST_conf"]) if "ST_conf" in S else None

    def check_first_order(self):
        if self.O1_indices is None:
            raise ValueError("No first order indices present")
        else:
            return True

    def check_second_order(self):
        if self.O2_indices is None:
            raise ValueError("No second order indices present")
        else:
            return True

    def check_total_order(self):
        if self.OT_indices is None:
            raise ValueError("No total order indices present")
        else:
            return True

    @classmethod
    def from_dicts(cls, Si: dict, P: dict):
        """Creates a SensitivityIndices object from the provided dictionary."""
        return cls(Si, P)

    def get_min_S2(self):
        """Gets the value of the minimum S2 index."""
        self.check_second_order()
        return np.amin(self.O2_indices)

    def get_argmin_S2(self):
        """Gets the location of the minimum S2 index."""
        self.check_second_order()
        full_index = np.argmin(self.O2_indices)
        return np.unravel_index(full_index, self.O2_indices.shape)

    def get_max_S2(self):
        """Gets the value of the maximum S2 index."""
        self.check_second_order()
        return np.amax(self.O2_indices)

    def get_argmax_S2(self):
        """Gets the location of the maximum S2 index."""
        self.check_second_order()
        full_index = np.argmax(self.O2_indices)
        return np.unravel_index(full_index, self.O2_indices.shape)

    @classmethod
    def from_json_dict(cls, js_data):
        return cls(js_data, {"names": js_data["names"]})

    @classmethod
    def from_json_file(cls, filepath: str):
        with open(filepath, "r", encoding="utf-8") as f:
            js_data = json.load(f)
        return cls.from_json_dict(js_data)

    def to_dict(self):
        return {
            "S1": self.O1_indices.tolist(),
            "S2": self.O2_indices.tolist(),
            "ST": self.OT_indices.tolist(),
            "S1_conf": self.O1_confidence.tolist(),
            "S2_conf": self.O2_confidence.tolist(),
            "ST_conf": self.OT_confidence.tolist(),
            "names": self.parameter_list,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_json_file(self, filepath: str):
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f)


class SADependentVariable(object):

    name: str
    # Ordered list of variable names defining inputs to calculate this
    # variables value
    inputs: list
    # Callable that computes this variables value given its inputs
    expr: callable

    def __init__(self, name: str, inputs: list, expr: callable):
        self.name = name
        self.inputs = inputs
        self.expr = expr

    def can_compute_with_inputs(self, known_inputs: dict):
        return set(self.inputs).issubset(known_inputs.keys())

    def compute(self, known_inputs: dict):
        if self.can_compute_with_inputs(known_inputs):
            input_vals = [known_inputs[v] for v in self.inputs]
            # TODO handle the case where we depend on a constant value and a
            # bounded or vectorized np.array input
            if any([isinstance(inputs, type(np.array)) for inputs in input_vals]):
                return np.array([self.expr(*inputs) for inputs in zip(*input_vals)])
            else:
                return self.expr(*input_vals)

        return None


class SAExecutionEnvironment(object):

    # The grfn in which SA is taking place
    grfn: GroundedFunctionNetwork
    # Ordered list of SADependentVariable. The order indicates the order of
    # computing their values such that newly computed dependent vars could be
    # passed into the next ones for computation.
    dependent_variables: list
    # Dictionary of constant val variables going from their name to value
    constant_variables: dict
    # List of output variable names we care about from the grfn
    outputs: list

    def __init__(
        self,
        grfn: GroundedFunctionNetwork,
        dependent_variables: list,
        constant_variables: dict,
        outputs: list,
    ):
        self.grfn = grfn
        self.dependent_variables = dependent_variables
        self.constant_variables = constant_variables
        self.outputs = outputs

    def __call__(self, input: dict):
        known_inputs = {**self.constant_variables, **input}

        # Compute the dependent variable values
        for v in self.dependent_variables:
            if v.can_compute_with_inputs(known_inputs):
                known_inputs[v.name] = v.compute(known_inputs)
            else:
                raise SensitivityAnalysisExecutionError(
                    f"Error: Unable to gather inputs needed to compute dependent variable {v.name}"
                )

        return self.grfn(known_inputs, desired_outputs=self.outputs)


class SensitivityAnalyzer(object):
    def __init__(self):
        pass

    @staticmethod
    def setup_problem_def(GrFN, B):
        """
        So not all bounds are created uniformly, we can have different types
        that are represented binarily or categorically and we can also have some
        conditions where a modeler may not want to include one of the inputs
        under sensitivity analysis
        """

        # Not sure we need to perform this "conversion" beyond checking len 0
        def convert_bounds(bound):
            num_bounds = len(bound)
            if num_bounds == 0:
                raise ValueError("Found input variable with 0 bounds")
            elif num_bounds == 1:
                # NOTE: still going to use a zero to 1 range for now
                return [0, 1]
            elif len(bound) == 2:
                if all([isinstance(b, Number) for b in bound]):
                    return bound
                else:
                    return [0, 1]
            else:
                return [0, 1]

        return {
            "num_vars": len(B),
            "names": [k for k in B.keys()],
            "bounds": [convert_bounds(v) for v in B.values()],
        }

    @classmethod
    def check_and_build_dependents_list(cls, initial_inputs: set, dependent_vars: list):
        """
        Takes a list of initial input variable names and a list of dependent variables
        that require some input to be computed. This method will compute if there
        is an ordering of the dependent variables such that you can compute them
        all successfully without some missing information. If so, it returns this
        ordering of the dependent vars. Otherwise, it raises an exception.

        Args:
            initial_inputs (set): Set of names of the initial input vars
            dependent_vars (list): List of dependent vars where we are checking computability

        Raises:
            SensitivityAnalysisExecutionError: If we deteremine dependent var
                computability is impossible

        Returns:
            list: The list of dependent vars ordered in the correct execution path
        """
        dependent_computation_order = [
            v for v in dependent_vars if all([n in initial_inputs for n in v.inputs])
        ]
        current_input_set = initial_inputs.union(
            {v.name for v in dependent_computation_order}
        )

        remaining_dependents = [
            v
            for v in dependent_vars
            if not all([n in initial_inputs for n in v.inputs])
        ]

        while len(remaining_dependents) != 0:
            newly_computabe = [
                v
                for v in remaining_dependents
                if all([name in current_input_set for name in v.inputs])
            ]

            if len(newly_computabe) == 0:
                raise SensitivityAnalysisExecutionError(
                    f"Error: unable to compute input sets for dependent variables '{[v.name for v in remaining_dependents]}'"
                )

            newly_computable_names = [v.name for v in newly_computabe]
            remaining_dependents = [
                v for v in remaining_dependents if v.name not in newly_computable_names
            ]
            current_input_set = current_input_set.union(set(newly_computable_names))
            dependent_computation_order.extend(newly_computabe)

        return dependent_computation_order

    @classmethod
    def build_execution(cls, G: GroundedFunctionNetwork, B: dict, I: dict, O: list):
        bounded_input_names = set(B.keys())
        input_keys = set(I.keys())

        # matching_keys = input_keys.intersection(bounded_input_names)
        # if len(matching_keys) > 0:
        #     raise SensitivityAnalysisInputError(
        #         f"Error: Provided keys as both bounded and normal input: {matching_keys}"
        #     )

        expected = B
        dependents = []
        constants = {}
        for k, v in I.items():
            if isinstance(v, SADependentVariable):
                dependents.append(v)
            else:
                constants[k] = v

        ordered_dependents = cls.check_and_build_dependents_list(
            set(expected).union(set(constants.keys())), dependents
        )

        return SAExecutionEnvironment(G, ordered_dependents, constants, O)

    # TODO Remove timeit decorators
    @staticmethod
    @timeit
    def __run_analysis(analyzer, *args, **kwargs):
        return analyzer(*args, **kwargs)

    @staticmethod
    @timeit
    def __run_sampling(sampler, *args, **kwargs):
        return sampler(*args, **kwargs)

    @classmethod
    @timeit
    def __execute_CG(cls, execution_env, samples, problem, C, V, *args, **kwargs):
        def create_input_vector(name, vector, var_types=None):
            if var_types is None:
                return vector

            type_info = var_types[name]
            if type_info[0] != str:
                return vector

            if type_info[0] == str:
                (str1, str2) = type_info[1]
                return np.where(vector >= 0.5, str1, str2)
            else:
                raise ValueError(f"Unrecognized value type: {type_info[0]}")

        # Create vectors of sample inputs to run through the model
        # vectorized_sample_list = np.split(samples, samples.shape[1], axis=1)
        vectorized_sample_list = np.transpose(samples)
        vectorized_input_samples = {
            name: create_input_vector(name, vector, var_types=V)
            for name, vector in zip(problem["names"], vectorized_sample_list)
        }

        outputs = execution_env(vectorized_input_samples)

        def parse_output(o):
            if isinstance(o, np.ndarray) and len(o.shape) > 1:
                return np.transpose(outputs["tma"])
            return [np.array(o)]

        ordered_output_vectors = [
            list_outputs
            for output in outputs.values()
            for list_outputs in parse_output(output)
        ]

        return ordered_output_vectors

    @classmethod
    def Si_from_Sobol(
        cls,
        N: int,
        G: GroundedFunctionNetwork,
        B: dict,
        I: dict,
        O: list = None,
        C: dict = None,
        V: dict = None,
        calc_2nd: bool = True,
        num_resamples=100,
        conf_level=0.95,
        seed=None,
        save_time: bool = False,
    ) -> dict:
        """Generates Sensitivity indices using the Sobol method
        Args:
            N: The number of samples to analyze when generating Si
            G: The GroundedFunctionNetwork to analyze
            B: A dictionary of bound information for the inputs of G
            I: A dictionary of initial input values for non-bounded inputs
            O: A list of output var names that we can optionally give for SA
            C: A dictionary of cover values for use when G is a FIB
            V: A dictionary of GrFN input variable types
            calc_2nd: A boolean that determines whether to include S2 indices
            save_time: Whether to return timing information
        Returns:
            A SensitivityIndices object containing all data from SALib analysis
        """
        prob_def = cls.setup_problem_def(G, B)

        (samples, sample_time) = cls.__run_sampling(
            saltelli.sample,
            prob_def,
            N,
            calc_second_order=calc_2nd,
            seed=seed,
        )

        exec_env = cls.build_execution(G, B, I, O)
        (Y, exec_time) = cls.__execute_CG(exec_env, samples, prob_def, C, V)

        results = list()
        for y in Y:
            (S, analyze_time) = cls.__run_analysis(
                sobol.analyze,
                prob_def,
                np.hstack(y),
                calc_second_order=True,
                num_resamples=100,
                conf_level=0.95,
                seed=None,
            )

            Si = SensitivityIndices(S, prob_def)
            results.append(Si)

        timing_tuple = (sample_time, exec_time, analyze_time)
        return results if not save_time else (results, timing_tuple)

    @classmethod
    def Si_from_FAST(
        cls,
        N: int,
        G: GroundedFunctionNetwork,
        B: dict,
        I: dict,
        C: dict = None,
        V: dict = None,
        M: int = 4,
        save_time: bool = False,
        verbose: bool = False,
        seed: int = None,
    ) -> dict:

        prob_def = cls.setup_problem_def(G, B)

        (samples, sample_time) = cls.__run_sampling(
            SAL.sample.fast_sampler.sample, prob_def, N, M=M, seed=seed
        )

        (Y, exec_time) = cls.__execute_CG(G, samples, prob_def, C, V)

        results = list()
        for y in Y:
            (S, analyze_time) = cls.__run_analysis(
                fast.analyze,
                prob_def,
                Y,
                M=M,
                print_to_console=False,
                seed=seed,
            )
            Si = SensitivityIndices(S, prob_def)
            results.append(Si)

        timing_tuple = (sample_time, exec_time, analyze_time)
        return results if not save_time else (results, timing_tuple)

    @classmethod
    def Si_from_RBD_FAST(
        cls,
        N: int,
        G: GroundedFunctionNetwork,
        B: dict,
        I: dict,
        C: dict = None,
        V: dict = None,
        M: int = 10,
        save_time: bool = False,
        verbose: bool = False,
        seed: int = None,
    ):

        prob_def = cls.setup_problem_def(G, B)

        (samples, sample_time) = cls.__run_sampling(
            latin.sample, prob_def, N, seed=seed
        )

        X = samples

        (Y, exec_time) = cls.__execute_CG(G, samples, prob_def, C, V)

        results = list()
        for y in Y:
            (S, analyze_time) = cls.__run_analysis(
                rbd_fast.analyze,
                prob_def,
                X,
                Y,
                M=M,
                print_to_console=False,
                seed=seed,
            )

            Si = SensitivityIndices(S, prob_def)
            results.append(Si)

        timing_tuple = (sample_time, exec_time, analyze_time)
        return results if not save_time else (results, timing_tuple)


def ISA(
    model: GroundedFunctionNetwork,
    bounds: dict,
    sample_size: int,
    sa_method: callable,
    max_iterations: int = 5,
) -> dict:
    MAX_GRAPH = nx.DiGraph()
    VAR_POI = dict()
    COLORS = [
        "#ffffff",
        "#ffffcc",
        "#ffeda0",
        "#fed976",
        "#feb24c",
        "#fd8d3c",
        "#fc4e2a",
        "#e31a1c",
        "#bd0026",
        "#800026",
    ]
    PBAR = tqdm(total=sum([3 ** i for i in range(max_iterations)]))

    def __add_max_var_node(max_var: str, max_s1_val: float, S1_scores: list) -> str:
        node_id = uuid4()
        clr_idx = round(max_s1_val * 10)
        MAX_GRAPH.add_node(
            node_id,
            fillcolor=COLORS[clr_idx],
            fontcolor="white" if clr_idx > 5 else "black",
            style="filled",
            label=f"{max_var}\n({max_s1_val:.2f})",
            S1_data=S1_scores,
        )

        return node_id

    def __get_max_S1(cur_bounds: dict) -> list:
        Si = sa_method(sample_size, model, cur_bounds, save_time=False)

        S1_tuples = list(zip(Si.parameter_list, list(Si.O1_indices)))
        return S1_tuples

    def __get_var_bound_breaks(cur_bounds: list, partitions: int = 3):
        num_bounds = len(cur_bounds)
        if num_bounds < 2:
            raise RuntimeError(f"Improper number of bounds: {num_bounds}")
        elif num_bounds == 2:
            (lower, upper) = cur_bounds
            interval_sz = (upper - lower) / partitions
            return [
                (lower + (i * interval_sz), lower + ((i + 1) * interval_sz))
                for i in range(partitions)
            ]
        else:
            return list(zip(cur_bounds[:-1], cur_bounds[1:]))

    def __get_new_bound_sets(bbreaks: list, cur_var: str, cur_bounds: dict):
        new_bounds_container = list()
        for bound in bbreaks:
            new_bounds = deepcopy(cur_bounds)
            new_bounds[cur_var] = deepcopy(bound)
            new_bounds_container.append(new_bounds)
        return new_bounds_container

    def __static_analysis_on_var(max_var: str) -> list:
        if max_var in VAR_POI:
            return VAR_POI[max_var]

        # Search over all function nodes that include max_var as an input
        model_max_node = model.input_name_map[max_var]
        succ_funcs = list(model.successors(model_max_node))
        new_poi_list = list()
        for succ_func_name in succ_funcs:
            func_ref = model.nodes[succ_func_name]["lambda_fn"]
            (def_line, cond_line, _) = inspect.getsource(func_ref).split("\n")

            # Stop search if not conditional statement
            if re.search(r"__condition__", def_line) is None:
                continue

            # Extract the simple conditional portion
            numeric = r"-?[0-9]+\.?[0-9]*"
            variable = r"[A-Za-z][_A-za-z]*"
            var_or_num = rf"({variable}|{numeric})"
            bool_ops = r"<|>|==|<=|>="
            cond = re.search(
                rf"{var_or_num} ({bool_ops}) {var_or_num}",
                cond_line,
            )

            # No simple conditional found
            if cond is None:
                continue

            # Extract the boolean comparison operand and operators
            cond = cond.group()
            operator = re.search(bool_ops, cond).group()
            (op1, op2) = [op.strip() for op in re.split(operator, cond)]

            # Create a new point-of-interest for max_var
            is_first_numeric = re.match(numeric, op1) is not None
            is_second_numeric = re.match(numeric, op2) is not None
            if is_first_numeric and not is_second_numeric:
                new_poi_list.append(float(op1))
            elif not is_first_numeric and is_second_numeric:
                new_poi_list.append(float(op2))

        VAR_POI[max_var] = new_poi_list
        return new_poi_list

    def __iterate_with_bounds(
        cur_bounds: dict,
        parent_id: str,
        pass_number: int,
        parent_var: str = None,
    ):
        # start by getting the current max S1 var and value
        S1_tuples = __get_max_S1(cur_bounds)
        (max_var, s1_val) = max(S1_tuples, key=lambda tup: tup[1])

        max_var_id = __add_max_var_node(max_var, float(s1_val), S1_tuples)
        if parent_var is not None:
            (l_b, u_b) = cur_bounds[parent_var]
            edge_label = f"[{l_b:.2f}, {u_b:.2f}]"
        else:
            edge_label = ""
        MAX_GRAPH.add_edge(parent_id, max_var_id, label=edge_label, object=cur_bounds)

        # Stop recursion with max iterations
        if pass_number == max_iterations:
            # PBAR.update(1)
            return

        if parent_var is not None:
            if max_var == parent_var:
                PBAR.update(1 + 3 ** (max_iterations - pass_number))
                return

        new_vals = __static_analysis_on_var(max_var)
        interval_points = deepcopy(list(cur_bounds[max_var]))
        (l_b, u_b) = cur_bounds[max_var]
        for val in new_vals:
            if l_b < val < u_b:
                interval_points.append(val)
        interval_points.sort()
        bound_breaks = __get_var_bound_breaks(interval_points)
        new_bound_sets = __get_new_bound_sets(bound_breaks, max_var, cur_bounds)

        for new_bounds in new_bound_sets:
            PBAR.update(1)
            __iterate_with_bounds(
                new_bounds,
                max_var_id,
                pass_number + 1,
                parent_var=max_var,
            )

    root_id = str(uuid4())
    root_label = "\n".join([f"{v}: [{b[0]}, {b[1]}]" for v, b in bounds.items()])

    MAX_GRAPH.add_node(root_id, shape="rectangle", label=root_label)
    __iterate_with_bounds(bounds, root_id, 1)
    PBAR.close()
    return MAX_GRAPH
