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


def find_related_nodes_of(nodes, g, mode, order=1,  topo=None, exclude_orig=False):
    """
    Finds all related nodes of a set by "mode" and optionally sorts them in topological order
    :param nodes: a list of nodes
    :param g: iGraph graph
    :param mode:    "in" to return ancestors of nodes,
                    "out" to return descendants of nodes,
                    "all" to return all connected nodes
    :param order:   for int, the maximum number of steps to take from nodes
                    for "max", will find all
    :param topo: topological order in which the return should be sorted
    :param exclude_orig: if True, the nodes in "nodes" will be removed from the return
    :return: the (optionally ordered) related nodes
    """
    # Check that mode is specified correctly
    if mode not in ["in", "out", "all"]:
        raise ValueError('Invalid mode specified, select from: "in", "out", or "all"')

    # Check that order is specified correctly, and compute g.vcount() if necessary
    if type(order) == int:
        order_to_pass = order
    elif order == "max":
        order_to_pass = g.vcount()
    else:
        raise ValueError('Invalid order specified, specify an integer or "max"')

    # Find the correct nodes
    related_list = g.neighborhood(nodes, order=order_to_pass, mode=mode)
    related_ind = list(set([node for related_nodes in related_list for node in related_nodes]))
    related_names = to_names(related_ind, g)

    # Remove the original nodes, if desired
    if exclude_orig:
        for node in nodes:
            related_names.remove(node)

    # Sort nodes into specified topological order, if desired
    if topo is not None:
        related_names_sorted = ts(related_names, topo)
        return related_names_sorted
    return related_names

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
    def d_sep_helper(include_pa, include_ch, el_name, an_xyz, stack, stack_names, stack_size, stack_top):
        visitable_parents = []
        visitable_children = []
        n_vis_pa = 0
        n_vis_ch = 0
        if include_pa:
            parents_unsort = find_related_nodes_of([el_name], g, "in")
            visitable_parents = list((set(parents_unsort) - {el_name}) & set(an_xyz))
            n_vis_pa = len(visitable_parents)
        if include_ch:
            children_unsort = find_related_nodes_of([el_name], g, "out")
            visitable_children = list((set(children_unsort) - {el_name}) & set(an_xyz))
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
        return (stack, stack_names, stack_size, stack_top)

    an_z = find_related_nodes_of(z, g, "in", order="max")
    an_xyz = find_related_nodes_of(list(set(x) | set(y) | set(z)), g,"in", order="max")
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
                (stack, stack_names, stack_size, stack_top) = d_sep_helper(include_pa=True, include_ch=True,
                                                                           el_name=el_name, an_xyz=an_xyz, stack=stack,
                                                                           stack_names=stack_names,
                                                                           stack_size=stack_size, stack_top=stack_top)
            elif not el:
                if not el_name_in_z:
                    (stack, stack_names, stack_size, stack_top) = d_sep_helper(include_pa=False, include_ch=True,
                                                                               el_name=el_name, an_xyz=an_xyz,
                                                                               stack=stack,
                                                                               stack_names=stack_names,
                                                                               stack_size=stack_size,
                                                                               stack_top=stack_top)
                if el_name in an_z:
                    (stack, stack_names, stack_size, stack_top) = d_sep_helper(include_pa=True, include_ch=False,
                                                                               el_name=el_name, an_xyz=an_xyz,
                                                                               stack=stack,
                                                                               stack_names=stack_names,
                                                                               stack_size=stack_size,
                                                                               stack_top=stack_top)
    return True


def make_cg(g, gamma):
    cg = observed_graph(g)
    # Create iGraph attributes keeping track of node/edge properties
    for node in cg.vs():
        node["orig_name"] = node["name"]
        node["val_assign"] = None
        node["int_var"] = None
    for edge in cg.es():
        edge["initial_edge"] = True
    initial_verts = cg.vs.select(int_var=None)
    obs_elist = cg.es.select(initial_edge=True)

    # First Bullet
    # Replicate graph for each intervention mentioned in gamma
    num_int_vars = 0
    int_vars_checked = []
    obs_edges_to_add = []
    for event in gamma:
        if event.int_var is not None and event.int_var not in int_vars_checked:
            num_int_vars = num_int_vars + 1
            int_vars_checked.append(event.int_var)
            for node in initial_verts:
                if node["orig_name"] == event.int_var:  # Case sensitive
                    va = event.val_assign
                else:
                    va = None
                cg.add_vertices(1, attributes={"name": f"{node['orig_name']}_{event.int_var}", "orig_name": node["name"],
                                               "val_assign": va, "int_var": event.int_var})

            for edge in obs_elist:
                vlist0 = cg.vs.select(orig_name=cg.vs(edge.tuple[0])["orig_name"][0])
                vlist1 = cg.vs.select(orig_name=cg.vs(edge.tuple[1])["orig_name"][0])
                for node0 in vlist0:
                    for node1 in vlist1:
                        if (node0["int_var"] == node1["int_var"]) and (node0["int_var"] is not None):
                            obs_edges_to_add.append((node0.index, node1.index))
                            break
    cg.add_edges(set(obs_edges_to_add), attributes={"description": ["O"]*len(obs_edges_to_add)})

    # Add Unobserved Edges
    g_unobs_elist = g.es.select(description="U")
    edge_sets = []
    new_unobs_elist = []
    for edge in g_unobs_elist:
        if set(edge.tuple) not in edge_sets:  # Trims the unobserved list down to include a pair of nodes only once
            edge_sets.append(set(edge.tuple))
            new_unobs_elist.append(edge)
    unobs_edges_to_add = []
    num_unobs_verts = 0
    for edge in new_unobs_elist:
        num_unobs_verts = num_unobs_verts + 1
        cg.add_vertices(1, attributes={"name": f"U_{num_unobs_verts}"})
        new_vert_indx = cg.vs.select(name=f"U_{num_unobs_verts}").indices[0]
        old_vert_name0 = g.vs(edge.tuple[0])["name"][0]
        old_vert_name1 = g.vs(edge.tuple[1])["name"][0]
        # For old vertex, find all vertices with the same original name, connect unobserved vertex to each instance
        verts_0 = cg.vs.select(orig_name=old_vert_name0)
        for vert in verts_0:
            if vert["val_assign"] is None:
                unobs_edges_to_add.append((new_vert_indx, vert.index))
        verts_1 = cg.vs.select(orig_name=old_vert_name1)
        for vert in verts_1:
            if vert["val_assign"] is None:
                unobs_edges_to_add.append((new_vert_indx, vert.index))
    for node in initial_verts:
        # if "U" not in parents_unsort(cg_node_info[i].orig_name, cg):
        i = node.index
        if not any(i in edge for edge in unobs_edges_to_add):
            cg.add_vertices(1, attributes={"name": f"U_{node['name']}"})
            new_vert_indx = cg.vs.select(name=f"U_{node['name']}").indices[0]
            # Find all nodes across parallel worlds
            verts_to_connect = cg.vs.select(orig_name=node["name"])
            for vert in verts_to_connect:
                if vert["val_assign"] is None:
                    unobs_edges_to_add.append((new_vert_indx, vert.index))
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
    int_var: str = None


@dataclass
class CGNode:
    orig_name: str = None
    val_assign: str = None
    int_var: str = None


class IDANotIdentifiable(Exception):
    pass


