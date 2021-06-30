from __future__ import annotations
import igraph
import copy
import numpy
from typing import List
from dataclasses import dataclass, field


def observed_graph(g):
    """
    Constructs a subgraph containing only observed edges
    :param g: Input graph
    :return: Subgraph containing only observed edges
    """
    g_obs = copy.deepcopy(g)
    unobs_edges = g_obs.es.select(description="U")
    g_obs.delete_edges(unobs_edges)
    return g_obs


def unobserved_graph(g):
    """
    Constructs an unobserved graph
    :param g: Input graph
    :return: unobserved graph
    """
    g_copy = copy.deepcopy(g)
    unobs_edges = g_copy.es.select(description="U")
    u1 = len(unobs_edges)
    if u1 > 0:
        u = g_copy.es.select(description="U")
        edges_to_remove = []
        for edge in u:
            edge_tuple = edge.tuple
            if edge_tuple[1] > edge_tuple[0]:
                edges_to_remove.append(edge.index)
        g_copy.delete_edges(edges_to_remove)
        e = g_copy.es.select(description="U")
        e_len = len(e)
        new_nodes = []
        for i in range(e_len):
            new_nodes.append(f"u_{{i + 1}}")
        g_copy.add_vertices(new_nodes, attributes={"description": ["U"] * e_len})
        edge_list = []

        # We have now inserted new unobserved nodes into the graph
        # We replace the unobserved bi-directed edges with new edges pointing away from the new unobserved nodes
        # a is the index of the new unobserved node
        # b and c are the two nodes that were previously connected by a bi-directed edge
        for i in range(e_len):  # Loop through unobserved edges
            a = g_copy.vs.select(name=new_nodes[i]).indices[0]
            b = e[i].tuple[0]
            edge_list.append((a, b))
            c = e[i].tuple[1]
            edge_list.append((a, c))
        g_copy.add_edges(edge_list, attributes={"description": ["O"] * len(edge_list)})
        obs_edges = g_copy.es.select(description_ne="U")
        g_unobs = g_copy.subgraph_edges(obs_edges, delete_vertices=False)
        return g_unobs
    return g


def ts(nodes, topo_order):  # topo must be a list of names
    """
    Orders nodes by their topological order
    :param nodes: Nodes to be ordered
    :param topo_order: Order to arrange nodes
    :return: Ordered nodes (indices)
    """
    node_set = set(nodes)
    return [n for n in topo_order if n in node_set]


def ancestors(node, g, topo):
    """
    Finds all ancestors of a node and orders them
    :param node: node (indicated by its index)
    :param g: graph
    :param topo: topological ordering
    :return: Ancestors of node in topological ordering topo
    """
    an_list = g.neighborhood(node, order=g.vcount(), mode="in")
    an_ind = list(set([a for ans in an_list for a in ans]))
    an_names = to_names(an_ind, g)
    an = ts(an_names, topo)
    return an


def ancestors_unsort(node, g):
    """
    Finds all ancestors of a node without the need for a topological ordering
    :param node: set of nodes of which to find ancestors
    :param g: graph
    :return: Ancestors of nodes
    """
    an_list = g.neighborhood(node, order=g.vcount(), mode="in")
    an_ind = list(set([a for ans in an_list for a in ans]))
    an_names = to_names(an_ind, g)
    return an_names


def parents_unsort(node, g_obs):
    """
    Finds the parents (unsorted) of a node
    :param node: node
    :param g_obs: graph
    :return: parents of node
    """
    pa_list = g_obs.neighborhood(node, order=1, mode="in")
    pa_ind = list(set([p for pas in pa_list for p in pas]))
    pa_names = to_names(pa_ind, g_obs)
    return pa_names


def children_unsort(node, g):
    """
    Finds the children (unsorted) of a node
    :param node: node
    :param g: graph
    :return: children of node
    """
    ch_list = g.neighborhood(node, order=1, mode="out")
    ch_ind = list(set([c for chs in ch_list for c in chs]))
    ch_names = to_names(ch_ind, g)
    return ch_names


# def descendents(node, g, topo):
#     """
#     Finds all descendants of a node and orders them
#     :param node: node (indicated by its index)
#     :param g: graph
#     :param topo: topological ordering
#     :return: Descendants of node in topological ordering topo
#     """
#     des_list = g.neighborhood(node, order=g.vcount(), mode="out")
#     des_ind = list(set([d for des in des_list for d in des]))
#     des_names = to_names(des_ind, g)
#     des = ts(des_names, topo)
#     return des
#
#
# def connected(node, g, topo):
#     """
#     Finds all neighbors of a node and orders them (all connected nodes)
#     :param node: node (indicated by its index)
#     :param g: graph
#     :param topo: topological ordering
#     :return: Neighbors of node in topological ordering topo
#     """
#     con_ind = list(numpy.concatenate(g.neighborhood(node, order=g.vcount(), mode="all")).flat)
#     con_names = to_names(con_ind, g)
#     con = ts(con_names, topo)
#     return con
#
#
# # Assume "O" and "U" are specified in "description" attribute
# def compare_graphs(g1, g2):
#     """
#     Determines if two graphs are the same (including edge descriptions)
#     :param g1: First graph
#     :param g2: Second graph
#     :return: T/F indicating if G1 is the same as G2
#     """
#     e1 = numpy.array(g1.get_edgelist())
#     n1 = numpy.shape(e1)[0]
#     e2 = numpy.array(g2.get_edgelist())
#     n2 = numpy.shape(e2)[0]
#     if n1 != n2:
#         return False
#     if "description" in g1.es.attributes():
#         e1 = numpy.append(e1, numpy.transpose([g1.es["description"]]), axis=1)
#     else:
#         e1 = numpy.append(e1, numpy.transpose([numpy.repeat("O", n1)]), axis=1)
#     if "description" in g2.es.attributes():
#         e2 = numpy.append(e2, numpy.transpose([g2.es["description"]]), axis=1)
#     else:
#         e2 = numpy.append(e2, numpy.transpose([numpy.repeat("O", n2)]), axis=1)
#     return numpy.array_equal(e1, e2)


# Edge Selection Function (for line 3 section of ID)
def eselect(x, g):
    """
    Determines which edges should remain when cutting incoming arrows to x
    :param x: list of vertices
    :param g: graph
    :return: list of edges to keep
    """
    edges = set(g.es.select().indices)
    to = set(g.es.select(_to_in=g.vs.select(name_in=x).indices).indices)
    frm = set(g.es.select(_from_in=g.vs.select(name_in=x).indices).indices)
    description = set(g.es.select(description="U").indices)
    selection = edges - (to | (frm & description))
    return list(selection)


def eselect2(g, x, z):
    """
    For use in compute_IDC. Selects all edges in g except incoming to x and outgoing from z.
    :param g: graph
    :param x: nodes
    :param z: nodes
    :return: The set of edges in g that are not incoming to x or outgoing from z.
    """
    edges = set(g.es.select().indices)
    to_x = set(g.es.select(_to_in=g.vs.select(name_in=x).indices).indices)
    from_z = set(g.es.select(_from_in=g.vs.select(name_in=z).indices).indices)
    selection = edges - to_x - from_z
    return selection


def get_expression(prob, start_sum=False, single_source=False, target_sym="^*("):
    """
    Converts a class probability object to LaTeX plaintext
    :param prob: an object of class probability
    :param start_sum: should a sum be started
    :param single_source: is there only one source?
    :param target_sym: ?  todo: fix this
    :return: LaTeX plaintext
    """
    p = ""
    s_print = len(prob.sumset) > 0
    if s_print:
        sum_string = ",".join(prob.sumset)
        if start_sum:
            p = f"{p}\\left(\\sum_{{{sum_string}}}"
        else:
            p = f"{p}\\sum_{{{sum_string}}}"
    if prob.fraction:
        f_num = get_expression(prob.num, start_sum=False, single_source=single_source, target_sym=target_sym)
        f_den = get_expression(prob.den, start_sum=False, single_source=single_source, target_sym=target_sym)
        p = f"{p}\\frac{{{f_num}}}{{{f_den}}}"
    # if prob.sum:
    #     p = f"{p}\\left("
    #     add_strings = []
    #     i = 1
    #     for child in prob.children:
    #         new_sum = False
    #         if child.product or child.sum:
    #             new_sum = True
    #         child_ge = get_expression(child, start_sum=new_sum, single_source=single_source, target_sym=target_sym)
    #         to_append = f"w_{{{i}}}^{{({child.weight})}}{child_ge}"
    #         add_strings.append(to_append)
    #         i = i + 1
    #     con_strings = "".join(add_strings)
    #     p = f"{p}{con_strings}\\right)"

    if prob.product:
        for child in prob.children:
            new_sum = False
            if child.product or child.sum:
                new_sum = True
            child_ge = get_expression(child, start_sum=new_sum, single_source=single_source, target_sym=target_sym)
            p = f"{p}{child_ge}"

    if not (prob.sum or prob.product or prob.fraction):
        p = f"{p}P"
        if len(prob.do) > 0:
            do_string = "".join([prob.do])
            p = f"{p}_{{{do_string}}}"
        var_string = ",".join(prob.var)
        if prob.domain > 0:
            if prob.dom == 1:
                p = f"{p}{target_sym}{var_string}"
            else:
                if single_source:
                    p = f"{p}({var_string}"
                else:
                    p = f"{p}^{{({str(prob.domain - 1)}}}({var_string}"
        else:
            p = f"{p}({var_string}"
        if len(prob.cond) > 0:
            cond_string = ",".join(prob.cond)  # prob.cond must have elements that are strings
            cond_string = f"\u007C{cond_string})"
        else:
            cond_string = ")"
        p = f"{p}{cond_string}"
    if s_print and start_sum:

        p = ",".join([p, "\\right)"])
    return p


def c_components(g, topo):
    """
    Finds c-components in graph g
    :param g: graph
    :param topo: topological ordering
    :return: list of c-components (each c-component is a list of nodes)
    """
    a = g.get_adjacency()
    n = a.shape[0]
    v = g.vs["name"]
    bidirected = []
    for i in range(0, n):
        for j in range(i+1, n):
            if a[i][j] >= 1 and a[j][i] >= 1:
                bidirected.append(i)
                bidirected.append(j)
    bidirected_edges = g.es.select(_within=bidirected)
    g_bidirected = g.subgraph_edges(bidirected_edges, delete_vertices=False)
    subgraphs = g_bidirected.decompose()
    cc = []
    cc_rank = []
    for subgraph in subgraphs:
        nodes = ts(subgraph.vs["name"], topo)
        cc.append(nodes)
        rank = 0
        for node in nodes:
            rank = rank + topo.index(node)
        cc_rank.append(rank)
    (cc_sorted, _) = list(map(list, zip(*sorted(zip(cc, cc_rank), key=lambda ab: ab[1], reverse=True))))
    return cc_sorted


def parse_joint(p, v, cond, var, topo):
    p_new = Probability()
    p_num = copy.deepcopy(p)
    p_num.sumset = ts(set(p.sumset) | (set(var) - set(v) - set(cond)), topo)
    if len(cond) > 0:
        p_den = copy.deepcopy(p)
        p_den.sumset = ts(set(p.sumset) | (set(var) - set(cond)), topo)
        p_new.fraction = True
        p_new.num = copy.deepcopy(p_num)
        p_new.den = copy.deepcopy(p_den)
    else:
        p_new = copy.deepcopy(p_num)
    return p_new


def to_names(indices, g):
    """
    converts vertex indices indices to vertex names
    :param indices: list of indices
    :param g: graph (with named nodes)
    :return: list of vertex names
    """
    name_list = g.vs["name"]
    name_sorted = [name_list[i] for i in indices]
    return name_sorted


def wrap_d_sep(g, x, y, z):
    """
    Does some quick checks before testing d-separation
    :param g: Graph
    :param x: nodes
    :param y: nodes
    :param z: nodes
    :return: T/F if x is separated from y given z in g
    """
    if x == y:
        return False
    if len(x) == 0 or len(y) == 0:
        return True
    return d_sep(g, x, y, z)


def d_sep(g, x, y, z):
    """
    From R package causaleffect:

    "Implements relevant path separation (rp-separation) for testing d-separation. For details, see:

    Relevant Path Separation: A Faster Method for Testing Independencies in Bayesian Networks
    Cory J. Butz, Andre E. dos Santos, Jhonatan S. Oliveira;
    Proceedings of the Eighth International Conference on Probabilistic Graphical Models,
    PMLR 52:74-85, 2016."

    :param g: graph
    :param x: nodes
    :param y: nodes
    :param z: nodes
    :return: T/F if x is separated from y given z in g
    """
    an_z = ancestors_unsort(z, g)
    an_xyz = ancestors_unsort(list(set(x) | set(y) | set(z)), g)
    stack_top = len(x)
    stack_size = max(stack_top, 64)
    stack = [False] * stack_size
    stack[0:stack_top] = [True] * len(range(0, stack_top))
    stack_names = [None] * stack_size
    stack_names[0:stack_top] = copy.deepcopy(x)
    visited_top = 0
    visited_size = 64
    visited = [False] * visited_size
    visited_names = [None] * visited_size
    is_visited = False
    while stack_top > 0:
        is_visited = False
        el = stack[stack_top - 1]
        el_name = stack_names[stack_top - 1]
        stack_top = stack_top - 1
        if visited_top > 0:
            for i in range(0, visited_top):
                if el == visited[i] and el_name == visited_names[i]:
                    is_visited = True
                    break
        if not is_visited:
            if el_name in y:
                return False
            visited_top = visited_top + 1
            if visited_top > visited_size:
                visited_old = copy.deepcopy(visited)
                visited_size_old = visited_size
                visited_names_old = copy.deepcopy(visited_names)
                visited_size = 2 * visited_size
                visited = [False] * visited_size
                visited[0:visited_size_old] = copy.deepcopy(visited_old)
                visited_names = [None] * visited_size
                visited_names[0:visited_size_old] = copy.deepcopy(visited_names_old)
            visited[visited_top - 1] = el
            visited_names[visited_top - 1] = el_name
            el_name_in_z = el_name in z
            if el and (not el_name_in_z):
                visitable_parents = list((set(parents_unsort([el_name], g)) - set([el_name])) & set(an_xyz))
                visitable_children = list((set(children_unsort([el_name], g)) - set([el_name])) & set(an_xyz))
                n_vis_pa = len(visitable_parents)
                n_vis_ch = len(visitable_children)
                if n_vis_pa + n_vis_ch > 0:
                    while n_vis_pa + n_vis_ch + stack_top > stack_size:
                        stack_old = copy.deepcopy(stack)
                        stack_names_old = copy.deepcopy(stack_names)
                        stack_size_old = stack_size
                        stack_size = 2 * stack_size
                        stack = [False] * stack_size
                        stack[0:stack_size_old] = copy.deepcopy(stack_old)
                        stack_names = [None] * stack_size
                        stack_names[0:stack_size_old] = copy.deepcopy(stack_names_old)
                    stack_add = stack_top + n_vis_pa + n_vis_ch
                    stack[stack_top:stack_add] = [True] * n_vis_pa + [False] * n_vis_ch
                    stack_names[stack_top:stack_add] = copy.deepcopy(visitable_parents) + copy.deepcopy(
                        visitable_children)
                    stack_top = stack_add
            elif not el:
                if not el_name_in_z:
                    visitable_children = list((set(children_unsort(el_name, g)) - set(el_name)) & set(an_xyz))
                    n_vis_ch = len(visitable_children)
                    if n_vis_ch > 0:
                        while n_vis_ch + stack_top > stack_size:
                            stack_old = copy.deepcopy(stack)
                            stack_size_old = stack_size
                            stack_names_old = copy.deepcopy(stack_names)
                            stack_size = 2 * stack_size
                            stack = [False] * stack_size
                            stack[0:stack_size_old] = copy.deepcopy(stack_old)
                            stack_names[0:stack_size_old] = copy.deepcopy(stack_names_old)
                        stack_add = stack_top + n_vis_ch
                        stack[stack_top:stack_add] = [False] * n_vis_ch
                        stack_names[stack_top:stack_add] = copy.deepcopy(visitable_children)
                        stack_top = stack_add
                if el_name in an_z:
                    visitable_parents = list((set(parents_unsort([el_name], g)) - set([el_name]) & set(an_xyz)))
                    n_vis_pa = len(visitable_parents)
                    if n_vis_pa > 0:
                        while n_vis_pa + stack_top > stack_size:
                            stack_old = copy.deepcopy(stack)
                            stack_size_old = stack_size
                            stack_names_old = copy.deepcopy(stack_names)
                            stack_size = 2 * stack_size
                            stack = [False] * stack_size
                            stack[0:stack_size_old] = copy.deepcopy(stack_old)
                            stack_names[0:stack_size_old] = stack_names_old
                        stack_add = stack_top + n_vis_pa
                        stack[stack_top:stack_add] = [True] * n_vis_pa
                        stack_names[stack_top:stack_add] = copy.deepcopy(visitable_parents)
                        stack_top = stack_add
    return True


def make_cg(g, gamma):
    g_obs = observed_graph(g)
    g_obs_elist = g_obs.es
    n_nodes = g_obs.vcount()
    cg = copy.deepcopy(g_obs)

    # Create table keeping track of node properties
    cg_node_info = []
    for i in range(n_nodes):
        node = CgNode(index=i, orig_name=g_obs.vs[i]["name"])
        cg_node_info.append(node)

    # First Bullet
    # Replicate graph for each submodel mentioned in gamma
    k = 1
    submodels_checked = []
    for event in gamma:
        if event.submodel is not None and event.submodel not in submodels_checked:
            submodels_checked.append(event.submodel)
            for i in range(n_nodes):
                if cg_node_info[i].orig_name == event.submodel:  # Case sensitive
                    va = event.submodel
                else:
                    va = None
                node = CgNode(index=i+k*n_nodes, orig_name=g_obs.vs[i]["name"], val_assign=va, submodel=event.submodel)
                cg_node_info.append(node)
                cg.add_vertices(1, attributes={"name": f"{node.orig_name}_{node.submodel}"})

            obs_edges_to_add = []
            for edge in g_obs_elist:
                obs_edges_to_add.append(tuple(x + k*n_nodes for x in edge.tuple))
            cg.add_edges(obs_edges_to_add, attributes={"description": ["O"]*len(obs_edges_to_add)})

            k = k + 1

    # Add Unobserved Edges
    n_verts_total = cg.vcount()
    g_unobs_elist = g.es.select(description="U")
    edge_sets = []
    new_unobs_elist = []
    for edge in g_unobs_elist:
        if set(edge.tuple) not in edge_sets:  # Trim the unobserved list down to include a pair of nodes only once
            edge_sets.append(set(edge.tuple))
            new_unobs_elist.append(edge.tuple)

    unobs_edges_to_add = []
    for edge in new_unobs_elist:
        n_verts_total = n_verts_total + 1
        cg.add_vertices(1, attributes={"name": "U"})
        new_vert_indx = n_verts_total - 1  # Index of the newly-added unobserved node
        old_vert_indx0 = edge[0]
        old_vert_indx1 = edge[1]
        for i in range(k):  # Connects new unobserved node to the old nodes, and the old nodes in all other sub-models
            if cg_node_info[old_vert_indx0+i*n_nodes].orig_name != cg_node_info[old_vert_indx0+i*n_nodes].submodel:
                unobs_edges_to_add.append((new_vert_indx, old_vert_indx0+i*n_nodes))
            if cg_node_info[old_vert_indx1+i*n_nodes].orig_name != cg_node_info[old_vert_indx1+i*n_nodes].submodel:
                unobs_edges_to_add.append((new_vert_indx, old_vert_indx1+i*n_nodes))

    # Adding unobserved nodes/edges connecting node in original graph to corresponding submodels
    for i in range(n_nodes):
        # if "U" not in parents_unsort(cg_node_info[i].orig_name, cg):
        if not any(i in edge for edge in unobs_edges_to_add):
            n_verts_total = n_verts_total + 1
            cg.add_vertices(1, attributes={"name": f"U_{cg_node_info[i].orig_name}"})
            new_vert_indx = n_verts_total - 1

            for j in range(k):  # For each submodel
                if cg_node_info[i+j*n_nodes].val_assign is None:
                    unobs_edges_to_add.append((new_vert_indx, cg_node_info[i+j*n_nodes].index))
    cg.add_edges(unobs_edges_to_add, attributes={"description": ["U"] * len(unobs_edges_to_add)})
    return cg





@dataclass(unsafe_hash=True)
class Probability:
    var: list = field(default_factory=list)
    cond: list = field(default_factory=list)
    sumset: list = field(default_factory=list)
    do: str = ""
    product: bool = False
    children: list = field(default_factory=list)
    fraction: bool = False
    domain: int = 0
    sum: bool = False
    weight: list = field(default_factory=list)
    num: Probability = None
    den: Probability = None


@dataclass(unsafe_hash=True)
class Call:
    y: str = ""
    x: str = ""
    z: str = ""
    z_prime: str = ""
    p: Probability = Probability()
    g: igraph.Graph = igraph.Graph()
    line: int = 0
    v: list = field(default_factory=list)
    id_check: bool = False
    ancestors: list = field(default_factory=list)
    w: list = field(default_factory=list)
    an_xbar: list = field(default_factory=list)
    s: list = field(default_factory=list)
    s_prime: list = field(default_factory=list)


@dataclass(unsafe_hash=True)
class TreeNode:
    root: Probability = Probability()
    call: Call = Call()
    children: List[TreeNode] = field(default_factory=list)


@dataclass(unsafe_hash=True)
class ResultsInternal:
    p: Probability = Probability()
    tree: TreeNode = TreeNode()


@dataclass(unsafe_hash=True)
class Results:
    query: dict = field(default_factory=dict)
    algorithm: str = ""
    p: str = ""
    tree: TreeNode = TreeNode()


@dataclass
class CF:
    node: str = None
    val_assign: str = None
    submodel: str = None


@dataclass
class CgNode:
    index: int = None
    orig_name: str = None
    val_assign: str = None
    submodel: str = None


class IDANotIdentifiable(Exception):
    pass


gamma = [CF("Y", "y", "X"), CF("X", "x_prime"), CF("Z", "z", "D"), CF("D", "d")]
graph_9a = igraph.Graph(edges=[[0, 1], [1, 2], [3, 4], [4, 2], [0, 2], [2, 0]], directed=True)
graph_9a.vs["name"] = ["X", "W", "Y", "D", "Z"]
graph_9a.es["description"] = ["O", "O", "O", "O", "U", "U"]
cg = make_cg(graph_9a, gamma)
print(cg)