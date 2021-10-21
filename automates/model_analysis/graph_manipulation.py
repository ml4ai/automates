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
    if prob.cf_p_prime is not None:
        p_prime = get_expression(prob.cf_frac_num, start_sum=False, single_source=single_source, target_sym=target_sym)
        delta = ",".join(prob.cf_delta)
        num = f"P'"
        den = f"P'({delta})"
        p = f"{num}/{den}, where P' = {p_prime}"
        return p
    if len(prob.subscript) > 0:
        subscript = ",".join(prob.subscript)
        variables = ",".join(prob.var)
        p = f"P_{{{subscript}}}({variables})"
        return p
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
    unobs_edges = g.es.select(description="U")
    g_unobs = copy.deepcopy(g.subgraph_edges(unobs_edges, delete_vertices=False))
    # print(g_unobs)  # todo: add edges pointing back to unobserved nodes

    unobs_edges_to_add = []
    if "description" in g.vertex_attributes():
        for node in g_unobs.vs():
            if node["description"] == "U":
                unobs_indx = node.index
                neighbors = find_related_nodes_of([node["name"]], g_unobs, "all", exclude_orig=True)
                for neighbor in neighbors:
                    neighbor_ind = g_unobs.vs.select(name=neighbor)[0].index
                    unobs_edges_to_add.append((neighbor_ind, unobs_indx))
        g_unobs.add_edges(unobs_edges_to_add, attributes={"description": ["U"] * len(unobs_edges_to_add)})

    subgraphs = g_unobs.decompose()
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

    if "description" in g.vertex_attributes():
        for component in cc_sorted:
            for node in component:
                node_info = g.vs.select(name=node)[0]

                # Removes unobserved nodes from c_components
                if node_info["description"] == "U":
                    component.remove(node)

                # Removes nodes fixed by intervention from c_components
                if "int_vars" in g.vertex_attributes():
                    if node_info["int_vars"] is not None:
                        if node_info["orig_name"] in node_info["int_vars"]:
                            component.remove(node)
            if len(component) == 0:
                cc_sorted.remove(component)
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


def wrap_d_sep(g, x, y, z=None):
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


def d_sep(g, x, y, z=None):
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

    if z is not None:
        an_z = find_related_nodes_of(z, g, "in", order="max")
        an_xyz = find_related_nodes_of(list(set(x) | set(y) | set(z)), g, "in", order="max")
    else:
        an_z = []
        an_xyz = find_related_nodes_of(list(set(x) | set(y)), g, "in", order="max")

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

            # Fix argument of type 'NoneType' is not iterable
            if z is not None:
                el_name_in_z = el_name in z
            else:
                el_name_in_z = False

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


def parallel_worlds(g, gamma):
    """
    The first step in the "make_cg" algorithm in Complete Identification Methods for the Causal Hierarchy, by
     Shpitser and Pearl.
    :param g: The original graph.
    :param gamma: A conjunction of counterfactual statements (represented as a list).
    :return: The "parallel worlds" graph
    """
    p_worlds = observed_graph(g)
    # Create iGraph attributes keeping track of node/edge properties
    for node in p_worlds.vs():
        node["orig_name"] = node["name"]
        node["obs_val"] = None
        node["int_vars"] = []
        node["int_values"] = []
    for edge in p_worlds.es():
        edge["initial_edge"] = True
    initial_verts = p_worlds.vs.select(int_vars=[])
    obs_elist = p_worlds.es.select(initial_edge=True)

    for event in gamma:
        if event.obs_val is not None and len(event.int_vars) == 0:
            node_to_obs = p_worlds.vs.select(name=event.orig_name)
            node_to_obs["obs_val"] = event.obs_val

    # Replicate graph for each intervention mentioned in gamma
    num_int_vars = 0
    int_vars_checked = []
    obs_edges_to_add = []
    for event in gamma:
        if len(event.int_vars) > 0 and event.int_vars not in int_vars_checked:
            num_int_vars = num_int_vars + 1
            int_vars_checked.append(event.int_vars)
            for node in initial_verts:
                ov = None
                if node["orig_name"] == event.orig_name:
                    ov = event.obs_val
                if node["orig_name"] in event.int_vars:  # untested change
                    ov = event.int_values
                p_worlds.add_vertices(1, attributes={"name": f"{node['orig_name']}_{event.int_vars}",
                                                     "orig_name": node["name"], "obs_val": ov,
                                                     "int_vars": [event.int_vars], "int_values": [event.int_values]})

            for edge in obs_elist:
                vlist0 = p_worlds.vs.select(orig_name=p_worlds.vs(edge.tuple[0])["orig_name"][0])
                vlist1 = p_worlds.vs.select(orig_name=p_worlds.vs(edge.tuple[1])["orig_name"][0])
                for node0 in vlist0:
                    for node1 in vlist1:
                        if (node0["int_vars"] == node1["int_vars"]) and (len(node0["int_vars"]) > 0):
                            obs_edges_to_add.append((node0.index, node1.index))
                            break
    p_worlds.add_edges(set(obs_edges_to_add), attributes={"description": ["O"] * len(obs_edges_to_add)})

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
        empty_list = []
        p_worlds.add_vertices(1, attributes={"name": f"U_{num_unobs_verts}", "description": "U"})
        new_vert_indx = p_worlds.vs.select(name=f"U_{num_unobs_verts}").indices[0]
        old_vert_name0 = g.vs(edge.tuple[0])["name"][0]
        old_vert_name1 = g.vs(edge.tuple[1])["name"][0]
        # For old vertex, find all vertices with the same original name, connect unobserved vertex to each instance
        verts_0 = p_worlds.vs.select(orig_name=old_vert_name0)
        for vert in verts_0:
            if vert["orig_name"] not in vert["int_vars"]:
                unobs_edges_to_add.append((new_vert_indx, vert.index))
        verts_1 = p_worlds.vs.select(orig_name=old_vert_name1)
        for vert in verts_1:
            if vert["orig_name"] not in vert["int_vars"]:
                unobs_edges_to_add.append((new_vert_indx, vert.index))
    for node in initial_verts:
        # if "U" not in parents_unsort(cg_node_info[i].orig_name, cg):
        i = node.index
        if not any(i in edge for edge in unobs_edges_to_add):
            p_worlds.add_vertices(1, attributes={"name": f"U_{node['name']}", "description": "U"})
            new_vert_indx = p_worlds.vs.select(name=f"U_{node['name']}").indices[0]
            # Find all nodes across parallel worlds
            verts_to_connect = p_worlds.vs.select(orig_name=node["name"])
            for vert in verts_to_connect:
                if vert["orig_name"] not in vert["int_vars"]:
                    unobs_edges_to_add.append((new_vert_indx, vert.index))
    p_worlds.add_edges(unobs_edges_to_add, attributes={"description": ["U"] * len(unobs_edges_to_add)})

    # Removes ancestors of variables set by intervention
    nodes_to_remove = []
    for node in p_worlds.vs():
        if node["int_vars"] is not None and len(node["int_vars"]) > 0:
            # print(node["name"], node["int_vars"])
            if node["orig_name"] in node["int_vars"]:
                for name in find_related_nodes_of([node["name"]], p_worlds, "in", order="max"):
                    # print(name)
                    # print(node["name"])
                    if name != node["name"]:
                        nodes_to_remove.append(name)
    p_worlds.delete_vertices(nodes_to_remove)
    return p_worlds


def merge_nodes(g, node1, node2, gamma):  # Make sure node1 and node2 are not just names
    """
    Merges node1 and node2 into one vertex, with all of the parents/children of node1 and node2 connected appropriately
    and updates gamma as necessary to accommodate the removed vertex

    :param g: graph
    :param node1: the vertex to be merged with node2
    :param node2: the vertex to be merged with node1
    :param gamma: counterfactual conjunction, represented as a list
    :return: updated graph g and updated gamma
    """
    if (node1["orig_name"] in node1["int_vars"]) and (node2["orig_name"] in node2["int_vars"]):
        if node1["int_values"] != node2["int_values"]:
            return g, "Inconsistent"
    ch_delete = find_related_nodes_of(node2["name"], g, "out", exclude_orig=True)
    ch_keep = find_related_nodes_of(node1["name"], g, "out", exclude_orig=True)
    ch = list(set(ch_delete)-set(ch_keep))

    deleted_node_info = {"name": node2["name"][0], "int_vars": node2["int_vars"][0], "obs_val": node2["obs_val"][0],
                         "orig_name": node2["orig_name"][0], "int_values": node2["int_values"][0]}
    g.delete_vertices(node2["name"])
    node_keep_index = node1.indices[0]
    edges_to_add = []

    # Children of deleted vertex attached appropriately to the kept vertex
    for child in ch:
        child_index = g.vs.select(name=child).indices[0]
        edges_to_add.append((node_keep_index, child_index))
    g.add_edges(edges_to_add, attributes={"description": ["O"] * len(edges_to_add)})

    # Rename events in gamma if necessary
    # print(deleted_node_info)
    # print(gamma)
    for event in gamma:
        if event.orig_name == deleted_node_info["orig_name"]:
            if event.int_vars == deleted_node_info["int_vars"]:
                if event.obs_val == deleted_node_info["obs_val"]:
                    if event.int_values == deleted_node_info["int_values"]:
                        event.orig_name = node1["orig_name"][0]
                        event.int_vars = node1["int_vars"][0]
                        event.obs_val = node1["obs_val"][0]
                        event.int_values = node1["int_values"][0]
    return g, gamma


def should_merge(g, node1, node2):
    pa1 = find_related_nodes_of(node1["name"], g, "in", exclude_orig=True)
    pa2 = find_related_nodes_of(node2["name"], g, "in", exclude_orig=True)
    # print("unmatched_parents:", list(set(pa1) ^ set(pa2)))  # todo: testing line

    # Lemma 24, Second condition: There is a bijection f from Pa(alpha) to Pa(beta) such that a parent gamma and
    # f(gamma) have the same domain of values
    if len(pa1) == len(pa2):
        unmatched_parents = list(set(pa1) ^ set(pa2))
        if len(unmatched_parents) == 0:
            # print("merged approved, identical parents")  # todo: testing line
            return True
        for pa in unmatched_parents:
            # check_pa_set = list(set(unmatched_parents)-set(pa))
            check_pa_set = copy.deepcopy(unmatched_parents)
            check_pa_set.remove(pa)
            for candidate in check_pa_set:
                # print("candidate name:", candidate, ", candidate obs_val:", g.vs.select(name=candidate)["obs_val"])
                # print("other name:", pa, ", other obs_val:", g.vs.select(name=pa)["obs_val"])
                if (g.vs.select(name=candidate)["obs_val"][0] is not None) \
                        or (g.vs.select(name=pa)["obs_val"][0] is not None):
                    if g.vs.select(name=candidate)["obs_val"] == g.vs.select(name=pa)["obs_val"]:
                        # unmatched_parents = list(set(unmatched_parents)-candidate)
                        unmatched_parents.remove(candidate)
                        # print("found bijective parent")  # todo: testing line
                        break
                if candidate == check_pa_set[-1]:
                    # print("no bijective parent")  # todo: testing line
                    return False
        # print("merge approved, all parents matched")  # todo: testing line
        return True
    # print("no matching parents")  # todo: testing line
    return False
    
    
def make_cg(g, gamma):
    # Construct parallel worlds graph
    cg = parallel_worlds(g, gamma)

    # Set of original vertices before parallel worlds and topological order of these vertices
    original_topo_indices = observed_graph(g).topological_sorting()
    original_topo_names = []
    for i in original_topo_indices:
        original_topo_names.append(g.vs[i]["name"])

    # Merge redundant vertices and update names in gamma if necessary
    gamma_prime = copy.deepcopy(gamma)
    for orig_node in original_topo_names:
        merge_candidates = cg.vs.select(orig_name=orig_node)["name"]
        while len(merge_candidates) > 1:
            # print("merge_candidates at beginning of loop:", merge_candidates)  # todo: testing line
            primary_node = cg.vs.select(name=merge_candidates[0])
            secondary_candidates = copy.deepcopy(merge_candidates)
            secondary_candidates.remove(merge_candidates[0])
            for secondary_node_name in secondary_candidates:
                secondary_node = cg.vs.select(name=secondary_node_name)
                # print("pair of nodes considered for merge:", primary_node["name"], secondary_node["name"])  # todo: testing line
                if should_merge(cg, primary_node, secondary_node):
                    (cg, gamma_prime) = merge_nodes(cg, primary_node, secondary_node, gamma_prime)
                    if gamma_prime == "Inconsistent":
                        return cg, gamma_prime
                    merge_candidates.remove(secondary_node_name)
            merge_candidates.remove(primary_node["name"][0])

    # Reduce graph to ancestors of vertices mentioned in gamma_prime
    nodes_in_gamma_prime = []
    for event in gamma_prime:
        if len(event.int_vars) > 0:
            nodes_in_gamma_prime.append(f"{event.orig_name}_{event.int_vars}")
        else:
            nodes_in_gamma_prime.append(event.orig_name)
    relevant_nodes = find_related_nodes_of(nodes_in_gamma_prime, cg, "in", "max")
    cg = cg.subgraph(relevant_nodes)

    # Remove unobserved nodes with only 1 child
    unobserved_nodes = cg.vs.select(description="U")["name"]
    for node in unobserved_nodes:
        if len(find_related_nodes_of([node], cg, "out", exclude_orig=True)) < 2:
            cg.delete_vertices(node)
    return cg, gamma_prime


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
    subscript: list = field(default_factory=list)
    cf_p_prime: Probability = None
    cf_delta: list = field(default_factory=list)


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
class CfCall:
    gamma: str = ""
    delta: str = ""
    p: Probability = Probability()
    g: igraph.Graph = igraph.Graph()
    line: int = 0
    v: list = field(default_factory=list)
    id_check: bool = False
    ancestors: list = field(default_factory=list)
    s: list = field(default_factory=list)
    s_prime: list = field(default_factory=list)


@dataclass(unsafe_hash=True)
class TreeNode:
    root: Probability = Probability()
    call: Call = Call()
    children: List[TreeNode] = field(default_factory=list)


@dataclass(unsafe_hash=True)
class CfTreeNode:
    root: Probability = Probability()
    call: Call = CfCall()
    children: List[CfTreeNode] = field(default_factory=list)


@dataclass(unsafe_hash=True)
class ResultsInternal:
    p: Probability = Probability()
    tree: TreeNode = TreeNode()


@dataclass(unsafe_hash=True)
class CfResultsInternal:
    p: Probability = Probability()
    tree: CfTreeNode = CfTreeNode()
    p_int: int = None
    p_message: str = ""


@dataclass(unsafe_hash=True)
class Results:
    query: dict = field(default_factory=dict)
    algorithm: str = ""
    p: str = ""
    tree: TreeNode = TreeNode()


@dataclass
class CF:
    orig_name: str = None
    obs_val: str = None
    int_vars: List[str] = field(default_factory=list)
    int_values: List[str] = field(default_factory=list)
    cond: str = None


class IDANotIdentifiable(Exception):
    pass
