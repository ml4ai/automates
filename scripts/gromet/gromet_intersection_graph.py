from dataclasses import dataclass, asdict
import json
from typing import NewType, Union, List
import os


UidIntersectionGraph = NewType('UidIntersectionGraph', str)
UidCommonNode = NewType('UidCommonNode', str)
UidGromet = NewType('UidGromet', str)
UidVariable = NewType('UidVariable', str)


@dataclass
class GrometIds:
    """
    Identify the two source GroMEt representations that will
    be compared. Source GroMEts are identified by their uid.
    Within this JSON format, fields representing content
    corresponding to the first model will be noted with filed
    names that have the prefix 'g1_', and similarly the second
    model with have field prefixed by 'g2_'.
    """
    g1_name: str
    g1_uid: UidGromet
    g2_name: str
    g2_uid: UidGromet


@dataclass
class CommonNode:
    """
    Nodes in the intersection graph representing variables
    from the source GroMEt that are considered the same.

    g1_variable and g2_variable are Lists (JSON arrays) in
    order to permit multiple variables along a path in either
    model being treated as identical (this happens when there
    is a path of variables within a model where the value
    value of the data along the path does not change).
    """
    uid: UidCommonNode
    # type: str  # one of: 'input', 'output', 'internal'
    g1_variable: List[UidVariable]
    g2_variable: List[UidVariable]


@dataclass
class OAPNode:
    """
    Overlapping Abstract Path Node.
    This node is an abstraction indicating that a collection
    of variables (and the operations along paths between those
    variables that modify the values, as represented by
    Expressions, Functions, Loops, etc...) from either model
    are not the same, but CommonNodes (variables from either
    model that are identified as matching) serve as inputs
    to and outputs from these paths. That is, although the
    details of what is computed along paths from either model
    may be different, there are overlapping/matching variables
    from either model that play the same role as input to and
    output from these paths.
    """
    uid: UidCommonNode
    g1_variables: Union[List[UidVariable], None]
    g2_variables: Union[List[UidVariable], None]


@dataclass
class NOAPNode:
    """
    Non-Overlapping Abstract Path Node.
    This node represents a collection of variables (and therefore
    all of the paths between these variables) from a single model,
    for which dataflow may go *in* to and/or *out* from, but this
    collection of paths does not have corresponding paths in the
    other model.
    """
    uid: UidCommonNode
    gromet_name: str
    variables: List[UidVariable]


@dataclass
class Edge:
    """
    Represent paths of dataflow from one CommonNode, OAPNode or
    NOAPNode to another.
    """
    type: str  # one of: 'equal', 'g1_subset_g2', 'g2_subset_g1', 'no_overlap'
    src: UidCommonNode
    dst: UidCommonNode


@dataclass
class GrometIntersectionGraph:
    """
    The top-level JSON object representing the Gromet Intersection
    Graph.
    """
    uid: UidIntersectionGraph
    gromet_ids: GrometIds

    common_nodes: List[CommonNode]
    oap_nodes: Union[List[OAPNode], None]
    noap_nodes: Union[List[NOAPNode], None]
    edges: List[Edge]


# -----------------------------------------------------------------------------
# Utils
# -----------------------------------------------------------------------------

def gig_to_json(gig: GrometIntersectionGraph,
                tgt_file: Union[str, None] = None,
                tgt_root: Union[str, None] = None):
    if tgt_file is None:
        tgt_file = f"gig__{gig.gromet_ids.g1_name}-{gig.gromet_ids.g2_name}.json"
    if tgt_root is not None:
        tgt_file = os.path.join(tgt_root, tgt_file)
    json.dump(asdict(gig),
              open(tgt_file, "w"),
              indent=2)
