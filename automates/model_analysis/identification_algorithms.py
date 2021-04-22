import igraph
import numpy
import graph_manipulation as gm
from copy import deepcopy


def compute_ID(y, x, p, g, g_obs, v, topo, tree):
    """
    Performs Shpitser and Pearl's ID algorithm
    :param y: value assignment outcome
    :param x: value assignment intervention
    :param p: probability object
    :param g: full graph
    :param g_obs: observed graph
    :param v: vertices todo: needs to be names
    :param topo: topological ordering
    :param tree: object to store line-by-line summary
    :return: P(y | do(x)) if y is identifiable or failure.
                Note that the output needs to be read by get_expression
    """
    to = None
    frm = None
    description = None
    tree = gm.TreeNode()
    if (len(p.var) == 0) and (not (p.product or p.fraction)):
        tree.call = gm.Call(y=y, x=x, p=gm.Probability(var=v), g=g, line=0, v=v, id_check=False)
    else:
        tree.call = gm.Call(y=y, x=x, p=p, g=g, line=0, v=v, id_check=False)

    # Line 1
    if len(x) == 0:
        if p.product or p.fraction:
            p.sumset = gm.ts(list((set(v) - set(y)) | set(p.sumset)), topo)
        else:
            p.var = y
        tree.call.line = 1
        tree.call.id_check = True
        tree.root = deepcopy(p)
        return gm.ResultsInternal(p=p, tree=tree)
    an = gm.ancestors(y, g_obs, topo)

    # Line 2
    if len(set(v) - set(an)) != 0:
        g_an = g.subgraph(an)
        g_an_obs = gm.observed_graph(g_an)
        if p.product or p.fraction:
            p.sumset = gm.ts(list((set(v) - set(an)) | set(p.sumset)), topo)
        else:
            p.var = an
        nxt = compute_ID(y, gm.ts(set(x) & set(an), topo), p, g_an, g_an_obs, an, topo, gm.TreeNode())
        tree.children.append(nxt.tree)
        tree.call.line = 2
        tree.call.id_check = nxt.tree.call.id_check
        tree.call.ancestors = an
        return gm.ResultsInternal(p=nxt.p, tree=tree)

    # Line 3
    g_xbar_elist = gm.eselect(x, g)
    g_xbar = g.subgraph_edges(g_xbar_elist, delete_vertices=False)
    an_xbar = gm.ancestors(y, gm.observed_graph(g_xbar), topo)
    w = gm.ts(list(set(v) - set(x) - set(an_xbar)), topo)
    w_len = len(w)
    if w_len != 0:
        nxt = compute_ID(y, gm.ts(list(set(x) | set(w)), topo), p, g, g_obs, v, topo, gm.TreeNode())
        tree.children.append(nxt.tree)
        tree.call.line = 3
        tree.call.id_check = nxt.tree.call.id_check
        tree.call.w = w
        tree.call.an_xbar = an_xbar
        return gm.ResultsInternal(p=nxt.p, tree=tree)

    # Line 4
    g_remove_x = g.subgraph(list(set(v) - set(x)))  # looks like its matching up to to R
    s = gm.c_components(g_remove_x, topo)
    if len(s) > 1:
        tree.call.line = 4
        product_list = []
        id_check_list = []
        for s_element in s:
            nxt = compute_ID(s_element, gm.ts(set(v) - set(s_element), topo), p, g, g_obs, v, topo, gm.TreeNode())
            product_list.append(nxt.p)
            id_check_list.append(nxt.tree.call.id_check)
            tree.children.append(nxt.tree)
        tree.call.id_check = all(id_check_list)
        return gm.ResultsInternal(p=gm.Probability(sumset=gm.ts(list(set(v) - set(y) - set(x)), topo), product=True, \
                                                   children=product_list), tree=tree)
    else:
        s_single = s[0]

        # Line 5
        cc = gm.c_components(g, topo)
        if cc[0] == v:
            tree.call.s = cc[0]
            tree.call.line = 5
            tree.call.id_check = False
            tree.root = deepcopy(p)
            return gm.ResultsInternal(p=p, tree=tree)

        # Line 6
        if s_single in cc:
            tree.call.line = 6
            tree.call.s = s_single
            s_single_length = len(s_single)
            product_list = []
            p_prod = gm.Probability()
            for node in s_single:
                node_topo_index = v.index(node)
                cond_set = v[0:node_topo_index]
                if p.product:
                    p_prod = gm.parse_joint(p, node, cond_set, v, topo)
                else:
                    p_prod = deepcopy(p)
                    p_prod.var = [node]
                    p_prod.cond = cond_set
                product_list.append(p_prod)
            product_list.reverse()
            if s_single_length > 1:
                prob_new = gm.Probability(sumset=gm.ts(set(s_single) - set(y), topo), product=True, children= \
                    product_list)
                tree.root = prob_new
                tree.call.id_check = True
                return gm.ResultsInternal(p=prob_new, tree=tree)
            if p_prod.product or p_prod.fraction:
                p_prod.sumset = gm.ts(list(set(p_prod.sumset) | (set(s_single) - set(y))), topo)
            else:
                p_prod.var = gm.ts(set(p_prod.var) - (set(p_prod.sumset) | (set(s_single) - set(y))), topo)
            tree.root = p_prod
            tree.call.id_check = True
            return gm.ResultsInternal(p=p_prod, tree=tree)

        # Line 7
        tree.call.s = s_single
        s_prime = None
        for component in cc:
            if set(s_single).issubset(set(component)):
                s_prime = component
                break
        tree.call.line = 7
        tree.call.s_prime = s_prime
        s_prime_length = len(s_prime)
        g_s_prime = g.subgraph(s_prime)
        g_s_prime_obs = gm.observed_graph(g_s_prime)
        product_list = []
        p_prod = gm.Probability()
        for node in s_prime:
            node_topo_index = v.index(node)
            cond_set = v[0:node_topo_index]
            if p.product:
                p_prod = gm.parse_joint(p, node, cond_set, v, topo)
            else:
                p_prod = deepcopy(p)
                p_prod.var = [node]
                p_prod.cond = cond_set
            product_list.append(p_prod)
        product_list.reverse()
        x_new = gm.ts(set(x) & set(s_prime), topo)
        if s_prime_length > 1:
            nxt = compute_ID(y, x_new, gm.Probability(product=True, children=product_list), g_s_prime, g_s_prime_obs, \
                             s_prime, topo, gm.TreeNode())
        else:
            nxt = compute_ID(y, x_new, product_list[0], g_s_prime, g_s_prime_obs, s_prime, topo, gm.TreeNode())
        tree.children.append(nxt.tree)
        tree.call.id_check = nxt.tree.call.id_check
        return gm.ResultsInternal(p=nxt.p, tree=tree)


def compute_IDC(y, x, z, p, g, g_obs, v, topo, tree):
    if len(p.var) == 0:
        tree.call = gm.Call(y=y, x=x, z=z, p=gm.Probability(var=v), g=g, v=v, id_check=False)
    else:
        tree.call = gm.Call(y=y, x=x, z=z, p=p, g=g, v=v, id_check=False)
