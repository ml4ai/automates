from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import singledispatch
from typing import Tuple
import re

from networkx import DiGraph
from automates.model_assembly.networks import GroundedFunctionNetwork


@dataclass(repr=False, frozen=True)
class LinkNode(ABC):
    uid: str
    content: str

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.content

    @staticmethod
    def from_dict(data: dict, element_type: str, grounding_information: dict):
        if element_type == "source":
            return CodeVarNode(data["uid"], data["content"], data["source"])
        elif element_type == "gl_src_var":
            src_vars = list()
            for src_var_uid in data["identifier_objects"]:
                src_var_data = [
                    src_var
                    for src_var in grounding_information["src"]
                    if src_var_uid == src_var["uid"]
                ][0]
                src_vars.append(
                    CodeVarNode(
                        src_var_data["uid"],
                        src_var_data["content"],
                        src_var_data["source"],
                    )
                )
            return GCodeVarNode(data["uid"], data["content"], tuple(src_vars))
        elif element_type == "gl_comm":
            comm_vars = list()
            for comm_var_uid in data["identifier_objects"]:
                comm_var_data = [
                    comm_var
                    for comm_var in grounding_information["comment"]
                    if comm_var_uid == comm_var["uid"]
                ][0]
                comm_vars.append(
                    CommSpanNode(
                        comm_var_data["uid"],
                        comm_var_data["content"],
                        comm_var_data["source"],
                    )
                )
            return GCommSpanNode(data["uid"], data["content"], tuple(comm_vars))
        elif element_type == "gl_eq_var":
            equation_nodes = list()
            for equation_node_uid in data["identifier_objects"]:
                equation_node_matches = [
                    eq
                    for eq in grounding_information["equation"]
                    if eq["uid"] == equation_node_uid
                ]
                if len(equation_node_matches) == 0:
                    continue
                equation_node = equation_node_matches[0]
                equation = None
                equation_index = -1
                if "equation_uid" in equation_node:
                    for eq in grounding_information["full_text_equation"]:
                        equation_index += 1
                        if eq["uid"] == equation_node["equation_uid"]:
                            equation = FullTextEquationNode(eq["uid"], eq["content"])
                            break
                equation_nodes.append(
                    EqnVarNode(
                        equation_node["uid"],
                        equation_node["content"],
                        equation,
                        equation_index,
                    )
                )

            return GEqnVarNode(data["uid"], data["content"], tuple(equation_nodes))

        elif element_type == "gvar":
            text_vars = list()
            for text_var_uid in data["identifier_objects"]:
                text_var_data = [
                    text_var
                    for text_var in grounding_information["text_var"]
                    if text_var_uid == text_var["uid"]
                ][0]
                # TODO I dont think TR produces this data anymore, do we need it?
                # query_string = ";".join(text_var_data["svo_query_terms"])
                text_vars.append(
                    TextVarNode(
                        text_var_data["source"],
                        text_var_data["content"],
                        TextExtraction(
                            text_var_data["spans"]["page"],
                            text_var_data["spans"]["block"],
                            tuple(
                                Span(s["char_begin"], s["char_end"])
                                for s in text_var_data["spans"]["spans"]
                            ),
                        ),
                    )
                )

            return GVarNode(data["uid"], data["content"], tuple(text_vars))
        # elif element_type == "text_span":
        #     return TextSpanNode(data["source"], data["content"])
        elif (
            element_type == "parameter_setting_via_idfr"
            or element_type == "int_param_setting_via_idfr"
            or element_type == "parameter_setting_via_cncpt"
            or element_type == "int_param_setting_via_cncpt"
        ):
            return ParameterSettingNode(
                data["uid"],
                data["content"],
                data["original_sentence"],
                data["source"],
                TextExtraction(
                    data["spans"]["page"],
                    data["spans"]["block"],
                    tuple(
                        Span(s["char_begin"], s["char_end"])
                        for s in data["spans"]["spans"]
                    ),
                ),
            )
        elif element_type == "unit_via_idfr" or element_type == "unit_via_cncpt":
            return UnitNode(
                data["uid"],
                data["content"],
                TextExtraction(
                    data["spans"]["page"],
                    data["spans"]["block"],
                    tuple(
                        Span(s["char_begin"], s["char_end"])
                        for s in data["spans"]["spans"]
                    ),
                ),
            )
        else:
            raise ValueError(f"Unrecognized link element type: {element_type}")

    @abstractmethod
    def get_table_rows(self, link_graph: DiGraph) -> list:
        return NotImplemented


@dataclass(repr=False, frozen=True)
class Span:
    char_begin: int
    char_end: int


@dataclass(frozen=True)
class TextExtraction:
    page: int
    block: int
    spans: Tuple[Span]


@dataclass(repr=False, frozen=True)
class ParameterSettingNode(LinkNode):

    original_sentence: str
    source: str
    text_extraction: TextExtraction

    def get_table_rows(self, link_graph: DiGraph) -> list:
        return None


@dataclass(repr=False, frozen=True)
class UnitNode(LinkNode):
    text_extraction: TextExtraction

    def get_table_rows(self, link_graph: DiGraph) -> list:
        return None


@dataclass(repr=False, frozen=True)
class CodeVarNode(LinkNode):
    source: str

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        # TODO the content no longer holds the var identifier. Is that correct?
        # (namespace, scope, basename, index) = self.content.split("::")
        # return "\n".join(
        #     [
        #         f"NAMESPACE: {namespace}",
        #         f"SCOPE: {scope}",
        #         f"NAME: {basename}",
        #         f"INDEX: {index}",
        #     ]
        # )
        return self.content

    def get_varname(self) -> str:
        (_, _, _, basename, _) = self.content.split("::")
        return basename

    def get_table_rows(self, L: DiGraph) -> list:
        gcode_var_span_nodes = [
            n for n in L.predecessors(self) if isinstance(n, GCodeVarNode)
        ]

        rows = list()
        for gcode_var_node in gcode_var_span_nodes:
            w_vc = L.edges[gcode_var_node, self]["weight"]
            for r in gcode_var_node.get_table_rows(L):
                scores = [
                    val
                    for key, val in r.items()
                    if key.endswith("_score") and val is not None
                ]
                w_row = min(w_vc, *scores)
                r.update({"vc_score": w_vc, "link_score": w_row})
                rows.append(r)

        return rows


@dataclass(repr=False, frozen=True)
class GCodeVarNode(LinkNode):
    source: list

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.content

    def get_varname(self) -> str:
        (_, _, _, basename, _) = self.content.split("::")
        return basename

    def get_table_rows(self, L: DiGraph) -> list:
        comm_span_nodes = [
            n for n in L.predecessors(self) if isinstance(n, CommSpanNode)
        ]

        rows = list()
        for comm_node in comm_span_nodes:
            w_vc = L.edges[comm_node, self]["weight"]
            for r in comm_node.get_table_rows(L):
                scores = [
                    val
                    for key, val in r.items()
                    if key.endswith("_score") and val is not None
                ]
                w_row = min(w_vc, *scores)
                r.update({"vc_score": w_vc, "link_score": w_row})
                rows.append(r)

        return rows


@dataclass(repr=False, frozen=True)
class TextVarNode(LinkNode):
    # TODO Do we need svo query information?
    # svo_query_str: str
    text_extraction: TextExtraction

    def get_docname(self) -> str:
        path_pieces = self.source.split("/")
        doc_data = path_pieces[-1]
        (docname, _) = doc_data.split(".pdf_")
        return docname

    # def get_svo_terms(self):
    #     return self.svo_query_str.split(";")

    def get_table_rows(self, L: DiGraph) -> list:
        # NOTE: nothing to do for now
        return []


@dataclass(repr=False, frozen=True)
class GVarNode(LinkNode):
    text_vars: tuple

    def get_text_vars(self):
        return self.text_vars

    def get_table_rows(self, L: DiGraph) -> list:
        text_vars = [t_var for t_var in self.text_vars]
        txt = [n.content for n in text_vars]

        eqn_span_nodes = [n for n in L.predecessors(self) if isinstance(n, EqnVarNode)]

        rows = list()
        for eqn_span in eqn_span_nodes:
            te_ct = L.edges[eqn_span, self]["weight"]
            for r in eqn_span.get_table_rows(L):
                r.update({"txt": txt, "te_score": te_ct})
                rows.append(r)
        else:
            rows.append({"txt": txt, "te_score": None})

        return rows


@dataclass(repr=False, frozen=True)
class CommSpanNode(LinkNode):
    source: str

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        tokens = self.content.strip().split()
        if len(tokens) <= 4:
            return " ".join(tokens)

        new_content = ""
        while len(tokens) > 4:
            new_content += "\n" + " ".join(tokens[:4])
            tokens = tokens[4:]
        new_content += "\n" + " ".join(tokens)
        return new_content

    def get_comment_location(self):
        (filename, sub_name, place) = self.source.split("; ")
        filename = filename[: filename.rfind(".f")]
        return f"{filename}::{sub_name}${place}"

    def get_table_rows(self, L: DiGraph) -> list:
        gvar_nodes = [n for n in L.predecessors(self) if isinstance(n, GCommSpanNode)]

        rows = list()
        for gvar_node in gvar_nodes:
            w_ct = L.edges[gvar_node, self]["weight"]
            for r in gvar_node.get_table_rows(L):
                r.update({"comm": str(self).replace("\n", " "), "ct_score": w_ct})
                rows.append(r)

        return rows


@dataclass(repr=False, frozen=True)
class GCommSpanNode(LinkNode):
    source: list

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        tokens = self.content.strip().split()
        if len(tokens) <= 4:
            return " ".join(tokens)

        new_content = ""
        while len(tokens) > 4:
            new_content += "\n" + " ".join(tokens[:4])
            tokens = tokens[4:]
        new_content += "\n" + " ".join(tokens)
        return new_content

    def get_comment_location(self):
        (filename, sub_name, place) = self.source.split("; ")
        filename = filename[: filename.rfind(".f")]
        return f"{filename}::{sub_name}${place}"

    def get_table_rows(self, L: DiGraph) -> list:
        gvar_nodes = [n for n in L.predecessors(self) if isinstance(n, GVarNode)]

        rows = list()
        for gvar_node in gvar_nodes:
            w_ct = L.edges[gvar_node, self]["weight"]
            for r in gvar_node.get_table_rows(L):
                r.update({"comm": str(self).replace("\n", " "), "ct_score": w_ct})
                rows.append(r)

        return rows


# @dataclass(repr=False, frozen=True)
# class TextSpanNode(LinkNode):
#     def __repr__(self):
#         return self.__str__()

#     def __str__(self):
#         tokens = self.content.strip().split()
#         if len(tokens) <= 4:
#             return " ".join(tokens)

#         new_content = ""
#         while len(tokens) > 4:
#             new_content += "\n" + " ".join(tokens[:4])
#             tokens = tokens[4:]
#         new_content += "\n" + " ".join(tokens)
#         return new_content

#     def __data_from_source(self) -> tuple:
#         path_pieces = self.source.split("/")
#         doc_data = path_pieces[-1]
#         return tuple(doc_data.split(".pdf_"))

#     def get_docname(self) -> str:
#         (docname, _) = self.__data_from_source()
#         return docname

#     def get_sentence_id(self) -> str:
#         (_, data) = self.__data_from_source()
#         (sent_num, span_start, span_stop) = re.findall(r"[0-9]+", data)
#         return

#     def get_table_rows(self, L: DiGraph) -> list:
#         # NOTE I dont believe text spans have any direct links besides gvars
#         return None


@dataclass(repr=False, frozen=True)
class FullTextEquationNode(LinkNode):
    def get_table_rows(self, L: DiGraph) -> list:
        # TODO
        return None


@dataclass(repr=False, frozen=True)
class EqnVarNode(LinkNode):
    full_text_equations: FullTextEquationNode
    equation_number: int

    def get_table_rows(self, L: DiGraph) -> list:
        return [{"eqn": str(self)}]


@dataclass(repr=False, frozen=True)
class GEqnVarNode(LinkNode):
    equation_nodes: list

    def get_table_rows(self, L: DiGraph) -> list:
        return [{"eqn": str(self)}]


def build_link_graph(grounding_information: dict) -> DiGraph:
    G = DiGraph()

    def report_bad_link(n1, n2):
        raise ValueError(f"Inappropriate link type: ({type(n1)}, {type(n2)})")

    @singledispatch
    def add_link_node(node):
        raise ValueError(f"Inappropriate node type: {type(node)}")

    @add_link_node.register
    def _(node: CodeVarNode):
        G.add_node(node, color="darkviolet")

    @add_link_node.register
    def _(node: GCodeVarNode):
        G.add_node(node, color="violet")

    @add_link_node.register
    def _(node: CommSpanNode):
        G.add_node(node, color="lightskyblue")

    @add_link_node.register
    def _(node: GCommSpanNode):
        G.add_node(node, color="blue")

    @add_link_node.register
    def _(node: EqnVarNode):
        G.add_node(node, color="orange")

    @add_link_node.register
    def _(node: GEqnVarNode):
        G.add_node(node, color="yellow")

    @add_link_node.register
    def _(node: ParameterSettingNode):
        G.add_node(node, color="green")

    @add_link_node.register
    def _(node: UnitNode):
        G.add_node(node, color="crimson")

    @add_link_node.register
    def _(node: GVarNode):
        if node not in G:
            for text_var in node.text_vars:
                G.add_node(text_var)
                G.add_edge(node, text_var)
            G.add_node(node, color="deeppink")

    @singledispatch
    def add_link(n1, n2, score):
        raise ValueError(f"Inappropriate node type: {type(n1)}")

    @add_link.register
    def _(n1: GCodeVarNode, n2, score):
        add_link_node(n1)
        add_link_node(n2)

        if isinstance(n2, GCommSpanNode):
            G.add_edge(n2, n1, weight=score)
        else:
            report_bad_link(n1, n2)

    @add_link.register
    def _(n1: CommSpanNode, n2, score):
        add_link_node(n1)
        add_link_node(n2)

        if isinstance(n2, GCommSpanNode):
            G.add_edge(n1, n2, weight=score)
        # elif isinstance(n2, GVarNode):
        #    G.add_edge(n2, n1, weight=score)
        else:
            report_bad_link(n1, n2)

    @add_link.register
    def _(n1: GCommSpanNode, n2, score):
        add_link_node(n1)
        add_link_node(n2)

        if isinstance(n2, CommSpanNode):
            G.add_edge(n1, n2, weight=score)
        elif isinstance(n2, GVarNode):
            G.add_edge(n2, n1, weight=score)
        else:
            report_bad_link(n1, n2)

    @add_link.register
    def _(n1: ParameterSettingNode, n2, score):
        add_link_node(n1)
        add_link_node(n2)

        if isinstance(n2, GVarNode):
            G.add_edge(n2, n1, weight=score)
        else:
            report_bad_link(n1, n2)

    @add_link.register
    def _(n1: UnitNode, n2, score):
        add_link_node(n1)
        add_link_node(n2)

        if isinstance(n2, GVarNode):
            G.add_edge(n2, n1, weight=score)
        else:
            report_bad_link(n1, n2)

    @add_link.register
    def _(n1: GEqnVarNode, n2, score):
        add_link_node(n1)
        add_link_node(n2)

        if isinstance(n2, GVarNode):
            G.add_edge(n1, n2, weight=score)
        else:
            report_bad_link(n1, n2)

    @add_link.register
    def _(n1: GVarNode, n2, score):
        add_link_node(n1)
        add_link_node(n2)

        if isinstance(n2, (ParameterSettingNode, UnitNode)):
            G.add_edge(n1, n2, weight=score)
        else:
            report_bad_link(n1, n2)

    def build_link_node(element, type):
        # Element ids are structured like: <uid>::<name>. We want just the uid.
        uid = element.split("::")[0]
        # Go to its item type and gets its data information
        node_data = [
            item for item in grounding_information[type] if item["uid"] == uid
        ][0]

        return LinkNode.from_dict(node_data, type, grounding_information)

    def update_type(found_type):
        # In link objects, the to/from node type is specified as
        # "param_setting_via_idfr" but in the top level grounding information
        # it is specified as "parameter_setting_via_idfr"
        if found_type == "param_setting_via_idfr":
            return "parameter_setting_via_idfr"
        elif found_type == "interval_param_setting_via_idfr":
            return "int_param_setting_via_idfr"
        elif found_type == "param_setting_via_cpcpt":
            return "parameter_setting_via_cncpt"
        elif found_type == "interval_param_setting_via_cpcpt":
            return "int_param_setting_via_cncpt"
        elif found_type == "source":
            return "gl_src_var"
        elif found_type == "equation":
            return "gl_eq_var"
        elif found_type == "comment":
            return "gl_comm"
        elif found_type == "unit_via_cpcpt":
            return "unit_via_cncpt"
        return found_type

    link_hypotheses = grounding_information["links"]
    for link_dict in link_hypotheses:

        link_type = link_dict["link_type"]
        (node_1_type, node_2_type) = map(update_type, tuple(link_type.split("_to_")))

        node1 = build_link_node(link_dict["element_1"], node_1_type)
        node2 = build_link_node(link_dict["element_2"], node_2_type)

        link_score = round(link_dict["score"], 3)
        add_link(node1, node2, link_score)

    return G


def extract_link_tables(L: DiGraph) -> dict:
    var_nodes = [n for n in L.nodes if isinstance(n, CodeVarNode)]

    tables = dict()
    for var_node in var_nodes:
        var_name = str(var_node)
        if var_name not in tables:
            table_rows = var_node.get_table_rows(L)
            table_rows.sort(
                key=lambda r: [
                    r[f"{key}_score"]
                    for key in ["vc", "ct", "te"]
                    if r[f"{key}_score"] is not None
                ],
                reverse=True,
            )
            tables[var_name] = table_rows

    return tables


def print_table_data(table_data: dict) -> None:
    for var_name, table in table_data.items():
        print(var_name)
        print("L-SCORE\tComment\tV-C\tText-span\tC-T\tEquation\tT-E")
        for row in table:
            row_data = [
                str(row["link_score"]),
                row["comm"],
                str(row["vc_score"]),
                row["txt"],
                str(row["ct_score"]),
                row["eqn"],
                str(row["te_score"]),
            ]
            print("\t".join(row_data))
        print("\n\n")
