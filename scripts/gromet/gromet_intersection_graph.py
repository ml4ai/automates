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
    g1_name: str
    g1_uid: UidGromet
    g2_name: str
    g2_uid: UidGromet


@dataclass
class CommonNode:
    uid: UidCommonNode
    type: str  # one of: 'input', 'output', 'internal'
    g1_variable: List[UidVariable]
    g2_variable: List[UidVariable]


@dataclass
class OAPNode:
    uid: UidCommonNode
    g1_variables: Union[List[UidVariable], None]
    g2_variables: Union[List[UidVariable], None]


@dataclass
class NOAPNode:
    uid: UidCommonNode
    gromet_name: str
    variables: List[UidVariable]


@dataclass
class Edge:
    type: str  # one of: 'equal', 'g1_subset_g2', 'g2_subset_g1', 'no_overlap'
    src: UidCommonNode
    dst: UidCommonNode


@dataclass
class GrometIntersectionGraph:
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
