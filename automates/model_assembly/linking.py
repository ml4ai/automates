from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import singledispatch
import re

from networkx import DiGraph


@dataclass(repr=False, frozen=True)
class LinkNode(ABC):
    source: str
    content: str
    content_type: str

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.content

    @staticmethod
    def from_dict(data: dict):
        args = (data["source"], data["content"], data["content_type"])
        element_type = data["type"]
        if element_type == "identifier":
            return CodeVarNode(*args)
        elif element_type == "comment_span":
            return CommSpanNode(*args)
        elif element_type == "equation_span":
            return EqnSpanNode(*args)
        elif element_type == "text_var":
            query_string = ";".join(data["svo_query_terms"])
            return TextVarNode(*args, query_string)
        elif element_type == "text_span":
            return TextSpanNode(*args)
        else:
            raise ValueError(f"Unrecognized link element type: {element_type}")

    @abstractmethod
    def get_table_rows(self, link_graph: DiGraph) -> list:
        return NotImplemented


@dataclass(repr=False, frozen=True)
class CodeVarNode(LinkNode):
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        (namespace, scope, basename, index) = self.content.split("::")
        return "\n".join(
            [
                f"NAMESPACE: {namespace}",
                f"SCOPE: {scope}",
                f"NAME: {basename}",
                f"INDEX: {index}",
            ]
        )

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
                w_row = min(w_vc, r["ct_score"], r["te_score"])
                r.update({"vc_score": w_vc, "link_score": w_row})
                rows.append(r)

        return rows


@dataclass(repr=False, frozen=True)
class TextVarNode(LinkNode):
    svo_query_str: str

    def get_docname(self) -> str:
        path_pieces = self.source.split("/")
        doc_data = path_pieces[-1]
        (docname, _) = doc_data.split(".pdf_")
        return docname

    def get_svo_terms(self):
        return self.svo_query_str.split(";")

    def get_table_rows(self, L: DiGraph) -> list:
        # NOTE: nothing to do for now
        return []


@dataclass(repr=False, frozen=True)
class CommSpanNode(LinkNode):
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
        txt_span_nodes = [
            n for n in L.predecessors(self) if isinstance(n, TextSpanNode)
        ]

        rows = list()
        for txt_node in txt_span_nodes:
            w_ct = L.edges[txt_node, self]["weight"]
            for r in txt_node.get_table_rows(L):
                r.update({"comm": str(self), "ct_score": w_ct})
                rows.append(r)

        return rows


@dataclass(repr=False, frozen=True)
class TextSpanNode(LinkNode):
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

    def __data_from_source(self) -> tuple:
        path_pieces = self.source.split("/")
        doc_data = path_pieces[-1]
        return tuple(doc_data.split(".pdf_"))

    def get_docname(self) -> str:
        (docname, _) = self.__data_from_source()
        return docname

    def get_sentence_id(self) -> str:
        (_, data) = self.__data_from_source()
        (sent_num, span_start, span_stop) = re.findall(r"[0-9]+", data)
        return

    def get_table_rows(self, L: DiGraph) -> list:
        eqn_span_nodes = [
            n for n in L.predecessors(self) if isinstance(n, EqnSpanNode)
        ]

        rows = list()
        for eqn_node in eqn_span_nodes:
            w_te = L.edges[eqn_node, self]["weight"]
            for r in eqn_node.get_table_rows(L):
                r.update({"txt": str(self), "te_score": w_te})
                rows.append(r)

        return rows


@dataclass(repr=False, frozen=True)
class EqnSpanNode(LinkNode):
    def get_table_rows(self, L: DiGraph) -> list:
        return [{"eqn": str(self)}]


def build_link_graph(link_hypotheses: list) -> DiGraph:
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
    def _(node: CommSpanNode):
        G.add_node(node, color="lightskyblue")

    @add_link_node.register
    def _(node: TextSpanNode):
        G.add_node(node, color="crimson")

    @add_link_node.register
    def _(node: EqnSpanNode):
        G.add_node(node, color="orange")

    @add_link_node.register
    def _(node: TextVarNode):
        G.add_node(node, color="deeppink")

    @singledispatch
    def add_link(n1, n2, score):
        raise ValueError(f"Inappropriate node type: {type(n1)}")

    @add_link.register
    def _(n1: CodeVarNode, n2, score):
        add_link_node(n1)
        add_link_node(n2)

        if isinstance(n2, CommSpanNode):
            G.add_edge(n2, n1, weight=score)
        else:
            report_bad_link(n1, n2)

    @add_link.register
    def _(n1: CommSpanNode, n2, score):
        add_link_node(n1)
        add_link_node(n2)

        if isinstance(n2, CodeVarNode):
            G.add_edge(n1, n2, weight=score)
        elif isinstance(n2, TextSpanNode):
            G.add_edge(n2, n1, weight=score)
        else:
            report_bad_link(n1, n2)

    @add_link.register
    def _(n1: TextSpanNode, n2, score):
        add_link_node(n1)
        add_link_node(n2)

        if isinstance(n2, EqnSpanNode):
            G.add_edge(n2, n1, weight=link_score)
        elif isinstance(n2, CommSpanNode):
            G.add_edge(n1, n2, weight=link_score)
        elif isinstance(n2, TextVarNode):
            G.add_edge(n2, n1, weight=link_score)
        else:
            report_bad_link(n1, n2)

    @add_link.register
    def _(n1: EqnSpanNode, n2, score):
        add_link_node(n1)
        add_link_node(n2)

        if isinstance(n2, TextSpanNode):
            G.add_edge(n1, n2, weight=link_score)
        else:
            report_bad_link(n1, n2)

    @add_link.register
    def _(n1: TextVarNode, n2, score):
        add_link_node(n1)
        add_link_node(n2)

        if isinstance(n2, TextSpanNode):
            G.add_edge(n1, n2, weight=link_score)
        else:
            report_bad_link(n1, n2)

    for link_dict in link_hypotheses:
        node1 = LinkNode.from_dict(link_dict["element_1"])
        node2 = LinkNode.from_dict(link_dict["element_2"])
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
                key=lambda r: (r["vc_score"], r["ct_score"], r["te_score"]),
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
