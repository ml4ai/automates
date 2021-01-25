from dataclasses import dataclass
from itertools import product
from typing import List
from abc import ABC
import json

import networkx as nx
import numpy as np

from automates.model_assembly.networks import (
    GroundedFunctionNetwork,
    CausalAnalysisGraph,
)


class GrFNIntersectionGraph(nx.DiGraph):
    def __init__(self):
        pass

    @classmethod
    def from_GrFN_comparison(
        cls,
        grfn1: GroundedFunctionNetwork,
        grfn2: GroundedFunctionNetwork,
        intersection: dict,
    ):
        """Creates a GrFN Intersection Graph class from two GrFNs and their overlapping elements.

        Args:
            grfn1 (GroundedFunctionNetwork): A GrFN used in the comparison
            grfn2 (GroundedFunctionNetwork): A second GrFN used in the comparison
            intersection (dict): The overlapping values (variable nodes and edges) between the two GrFNs
        """
        grfn_id2name = {uid: name for name, uid in intersection["grfn_ids"]}
        named_grfns = [(grfn_id2name[g.uid], g) for g in [grfn1, grfn2]]

        # These will be lists of list using the following structure:
        #     [ a list for each GrFN being compared ]
        #       [ a list of relevant elements in a GrFN ]
        per_grfn_input_node_uids = list()
        per_grfn_output_node_uids = list()
        per_grfn_uid_path_lists = list()
        for grfn_name, grfn in named_grfns:
            CAG = CausalAnalysisGraph.from_GrFN(grfn)
            var_nodes = {v.uid: v for v in CAG.nodes}
            extended_shared_input_nodes = (
                intersection["common_model_input_nodes"]
                + intersection["common_model_variable_nodes"]
            )
            shared_input_nodes = [
                var_nodes[node_pair[grfn_name]]
                for node_pair in extended_shared_input_nodes
            ]
            shared_output_nodes = [
                var_nodes[node_pair[grfn_name]]
                for node_pair in intersection["common_model_output_nodes"]
            ]

            shared_input_uids = [n.uid for n in shared_input_nodes]
            shared_output_uids = [n.uid for n in shared_output_nodes]

            # Takes the form of a list of paths where each path is
            # a list of node uids
            all_shared_io_paths = [
                [node.uid for node in shared_io_path]
                for in_node, out_node in product(
                    shared_input_nodes, shared_output_nodes
                )
                for shared_io_path in nx.all_simple_paths(
                    CAG, source=in_node, target=out_node
                )
            ]

            per_grfn_input_node_uids.append(shared_input_uids)
            per_grfn_output_node_uids.append(shared_output_uids)
            per_grfn_uid_path_lists(all_shared_io_paths)

        apn_member_sets = determine_abstract_path_nodes(
            per_grfn_input_node_uids, per_grfn_output_node_uids, per_grfn_uid_path_lists
        )

    def to_json(self):
        pass

    def to_json_file(self, filename: str):
        gig_json_data = self.to_json()
        json.dump(gig_json_data, open(filename, "w"))


@dataclass(repr=False, frozen=False)
class GenericIntersectionNode(ABC):
    uid: str

    def __hash__(self):
        """Provides a hash to uniquely identify any GIG node regardless of content

        Returns:
            str: stringified hash of the uuid for this node object
        """
        return str(hash(self.uid))

    def __eq__(self, other) -> bool:
        return self.uid == other.uid


@dataclass(repr=False, frozen=False)
class SharedVariableNode(GenericIntersectionNode):
    variables: List


@dataclass(repr=False, frozen=False)
class AbstractPathNode(GenericIntersectionNode):
    path_sets: List


def determine_abstract_path_nodes(
    shared_input_uid_lists: list,
    shared_outputs_uid_lists: list,
    input_output_path_lists: list,
):
    for input_uid_list, output_uid_list, io_paths in zip(
      shared_input_uid_lists,
      shared_outputs_uid_lists,
      input_output_path_lists):
        all_intersection_nodes = list(set(
            [node for path in io_paths for node in path]
        ))

    return NotImplemented
