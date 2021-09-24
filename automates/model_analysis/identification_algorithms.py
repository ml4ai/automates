import igraph
import numpy
import automates.model_analysis.graph_manipulation as gm
from copy import deepcopy


# expr, simp, steps, primes and prune options from causal.effect in R are not implemented here
def identifiability(y, x, g, z=None, steps=False, stop_on_noid=True):
    """
    Performs the appropriate Shpitser and Pearl identification algorithm (ID or IDC)
    :param y: value assignment outcome
    :param x: value assignment intervention
    :param g: graph
    :param z: value assignment conditional
    :param steps: should a summary of the algorithm appear in output?
    :param stop_on_noid: should causal_effect halt when non-identifiability is determined?
    :return: P(y |do(x), z) in LaTeX code
    """
    if "description" not in g.edge_attributes():
        g.es["description"] = numpy.repeat("O", len(g.es))
    g_obs = gm.observed_graph(g)
    if not g_obs.is_dag():
        raise ValueError("Graph 'G' is not a DAG.")
    topo_ind = g_obs.topological_sorting()
    topo = gm.to_names(topo_ind, g_obs)
    if len(set(y) - set(topo)) > 0:
        raise ValueError("Set 'y' contains variables not present in the graph.")
    if len(set(x) - set(topo)) > 0:
        raise ValueError("Set 'x' contains variables not present in the graph.")
    if z is not None:
        if len(set(z) - set(topo)) > 0:
            raise ValueError("Set 'z' contains variables not present in the graph.")
    if len(set(x) & set(y)) > 0:
        raise ValueError("Sets 'x' and 'y' are not disjoint.")
    if z is not None:
        if len(set(y) & set(z)) > 0:
            raise ValueError("Sets 'y' and 'z' are not disjoint.")
        if len(set(x) & set(z)) > 0:
            raise ValueError("Sets 'x' and 'z' are not disjoint.")
    if z is None:
        res = compute_ID(y, x, gm.Probability(), g, g_obs, topo, topo, gm.TreeNode())
        algo = "id"
        res_prob = res.p
    else:
        res = compute_IDC(y, x, z, gm.Probability(), g, g_obs, topo, topo, gm.TreeNode())
        algo = "idc"
        res_num = deepcopy(res.p)
        res_den = deepcopy(res_num)
        res_den.sumset = list(set(y) | set(res_den.sumset))
        res_prob = gm.Probability(fraction=True)
        res_prob.num = deepcopy(res_num)
        res_prob.den = deepcopy(res_den)

    res_tree = res.tree
    if res.tree.call.id_check:
        output = gm.Results(query={"y": y, "x": x, "z": z}, algorithm=algo, p=gm.get_expression(res_prob),
                            tree=res_tree)
        if steps:
            return output
        return output.p
    else:
        if stop_on_noid:
            raise gm.IDANotIdentifiable("Not Identifiable")
        output = gm.Results(query={"y": y, "x": x, "z": z}, algorithm=algo, p="", tree=res_tree)
        if steps:
            return output
        return output.p


def compute_ID(y, x, p, g, g_obs, v, topo, tree):
    """
    Performs Shpitser and Pearl's ID algorithm
    :param y: value assignment outcome
    :param x: value assignment intervention
    :param p: probability object
    :param g: full graph
    :param g_obs: observed graph
    :param v: vertices
    :param topo: topological ordering
    :param tree: object to store line-by-line summary
    :return: P(y | do(x)) if y is identifiable or failure.
                Note that the output needs to be read by get_expression
    """
    tree = gm.TreeNode()
    if (len(p.var) == 0) and (not (p.product or p.fraction)):
        p = gm.Probability(var=v)
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
    an = gm.find_related_nodes_of(y, g_obs, "in", order="max", topo=topo)

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
    an_xbar = gm.find_related_nodes_of(y, gm.observed_graph(g_xbar), "in", order="max", topo=topo)
    w = gm.ts(list(set(v) - set(x) - set(an_xbar)), topo)
    w_len = len(w)
    if w_len != 0:
        nxt = compute_ID(y, gm.ts(list(set(x) | set(w)), topo), p, g, g_obs, v, topo, gm.TreeNode())
        tree.children.append(deepcopy(nxt.tree))
        tree.call.line = 3
        tree.call.id_check = nxt.tree.call.id_check
        tree.call.w = w
        tree.call.an_xbar = an_xbar
        return gm.ResultsInternal(p=nxt.p, tree=tree)

    # Line 4
    g_remove_x = g.subgraph(list(set(v) - set(x)))
    s = gm.c_components(g_remove_x, topo)
    if len(s) > 1:
        tree.call.line = 4
        product_list = []
        id_check_list = []
        for s_element in s:
            nxt = compute_ID(s_element, gm.ts(set(v) - set(s_element), topo), p, g, g_obs, v, topo, gm.TreeNode())
            product_list.append(deepcopy(nxt.p))
            id_check_list.append(deepcopy(nxt.tree.call.id_check))
            tree.children.append(deepcopy(nxt.tree))
        tree.call.id_check = all(id_check_list)
        return gm.ResultsInternal(p=gm.Probability(sumset=gm.ts(list(set(v) - set(y) - set(x)), topo), product=True,
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
                product_list.append(deepcopy(p_prod))
            product_list.reverse()
            if s_single_length > 1:
                prob_new = gm.Probability(sumset=gm.ts(set(s_single) - set(y), topo), product=True,
                                          children=product_list)
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
        if s_prime is None:
            raise RuntimeError("s_prime component not identified in cc")
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
                p_prod = gm.parse_joint(p, node, cond_set, v, topo)  # todo: check this
            else:
                p_prod = deepcopy(p)  # todo: check this
                p_prod.var = [node]
                p_prod.cond = cond_set
            product_list.append(deepcopy(p_prod))
        product_list.reverse()
        x_new = gm.ts(set(x) & set(s_prime), topo)
        if s_prime_length > 1:
            p_nxt = gm.Probability(product=True, children=product_list)
        else:
            p_nxt = product_list[0]
        nxt = compute_ID(y, x_new, p_nxt, g_s_prime, g_s_prime_obs, s_prime, topo, gm.TreeNode())
        tree.children.append(deepcopy(nxt.tree))
        tree.call.id_check = nxt.tree.call.id_check
        return gm.ResultsInternal(p=nxt.p, tree=tree)


def compute_IDC(y, x, z, p, g, g_obs, v, topo, tree):
    if len(p.var) == 0:
        p = gm.Probability(var=v)
    tree.call = gm.Call(y=y, x=x, z=z, p=p, g=g, v=v, id_check=False)
    g_xz = gm.unobserved_graph(g)
    elist = gm.eselect2(g_xz, x, z)
    g_xz = g_xz.subgraph_edges(elist, delete_vertices=False)
    for node in z:
        cond = list(set(z) - set(node))
        if gm.wrap_d_sep(g_xz, y, [node], list(set(x) | set(cond))):
            tree.call.line = 9
            tree.call.z_prime = node
            nxt = compute_IDC(y, gm.ts(set(x) | set(node), topo), cond, p, g, g_obs, v, topo, gm.TreeNode())
            tree.children.append(deepcopy(nxt.tree))
            tree.call.id_check = nxt.tree.call.id_check
            return gm.ResultsInternal(p=nxt.p, tree=tree)
    nxt = compute_ID(gm.ts(set(y) | set(z), topo), x, p, g, g_obs, v, topo, gm.TreeNode())
    tree.call.line = 10
    tree.call.id_check = nxt.tree.call.id_check
    tree.children.append(nxt.tree)
    return gm.ResultsInternal(p=nxt.p, tree=tree)


def cf_identifiability(g, gamma, delta=None, steps=False, stop_on_noid=True):
    if "description" not in g.edge_attributes():
        g.es["description"] = numpy.repeat("O", len(g.es))

    g_obs = gm.observed_graph(g)
    if not g_obs.is_dag():
        raise ValueError("Graph 'G' is not a DAG.")

    topo_ind = g_obs.topological_sorting()
    topo = gm.to_names(topo_ind, g_obs)

    if delta is not None:
        res = cf_IDC(g, gamma, delta)
        algo = "cf_IDC"
    else:
        res = cf_ID(g, gamma, topo)
        algo ="cf_ID"

    res_tree = res.tree
    if len(res.p_message) > 0:
        if res.p_int is not None:
            res_prob = f"{res.p_message}, probability is {res}"
        else:
            res_prob = res.p_message
    else:
        res_prob = gm.get_expression(res.p)
    if res.tree.call.id_check:
        output = gm.Results(query={"gamma": gamma, "delta": delta}, algorithm=algo, p=res_prob, tree=res_tree)
        if steps:
            return output
        return output.p
    else:
        if stop_on_noid:
            raise gm.IDANotIdentifiable("Not Identifiable")
        output = gm.Results(query={"gamma": gamma, "delta": delta}, algorithm=algo, p="", tree=res_tree)
        if steps:
            return output
        return output.p


def cf_ID(g, gamma, v, p=gm.Probability(), tree=gm.CfTreeNode()):
    if (len(p.var) == 0) and (not (p.product or p.fraction)):
        p = gm.Probability(var=v)
    tree.call = gm.CfCall(gamma=gamma, p=p, g=g, line=0, v=v, id_check=False)

    # Line 1
    if len(gamma) == 0:
        tree.call.line = 1
        tree.call.id_check = True
        return gm.CfResultsInternal(p, tree, 1, "gamma is empty")

    for event in gamma:
        if event.orig_name in event.int_vars:

            # Line 2
            if event.obs_val not in event.int_values:
                tree.call.line = 2
                tree.call.id_check = True
                return gm.CfResultsInternal(p, tree, 0, "Violates Axiom of Effectiveness, gamma is inconsistent")

            # Line 3
            if event.obs_val in event.int_values:
                nxt = cf_ID(g, gamma.remove(event), v, p)
                tree.children.append(deepcopy(nxt.tree))
                tree.call.line = 3
                tree.call.id_check = nxt.tree.call.id_check
                return gm.CfResultsInternal(nxt.p, tree, nxt.p_int, nxt.p_message)

    # Line 4
    (cg, gamma_prime) = gm.make_cg(g, gamma)

    # Line 5
    if gamma_prime == "Inconsistent":
        tree.call.line = 5
        tree.call.id_check = True
        return gm.CfResultsInternal(p, tree, 0, "gamma_prime is inconsistent")

    # Line 6
    cg_obs = gm.observed_graph(cg)
    cg_topo_ind = cg_obs.topological_sorting()
    cg_topo = gm.to_names(cg_topo_ind, cg_obs)
    s = gm.c_components(cg, cg_topo)
    cg_obs_nodes = [node for component in s for node in component]
    if len(s) > 1:
        tree.call.line = 6
        product_list = []
        id_check_list = []
        for s_element in s:
            s_el_orig_names = []
            for node in s_element:
                s_el_orig_names.append(cg.vs.select(name=node)[0]["orig_name"])

            # Observed variables, with those mentioned in c-component removed
            subscript_variables = list(set(cg_obs_nodes)-set(s_element))
            subscript_orig_vars = []
            for var in subscript_variables:
                subscript_orig_vars.append(cg.vs.select(name=var)[0]["orig_name"])

            # Subscripts should be in ancestors of nodes in c-component
            for orig_var in subscript_orig_vars:
                if orig_var not in gm.find_related_nodes_of(s_el_orig_names, g, "in", "max"):
                    subscript_orig_vars.remove(orig_var)

            # Subscripts should not be redundant (should not be ancestors of one-another)
            for orig_var in subscript_orig_vars:
                if orig_var in gm.find_related_nodes_of(list(set(subscript_orig_vars)-orig_var), g, "in", "max"):
                    subscript_orig_vars.remove(orig_var)

            s_el_info = cg.vs.select(name_in=s_element)
            nxt_gamma = []
            for node in s_el_info:
                int_vars = node["int_vars"]
                int_values = node["int_values"]
                for subscript in subscript_orig_vars:
                    if subscript not in int_vars:
                        int_vars.append(subscript)  # todo: unsure about this
                        int_values.append(None)  # todo: unsure about this
                nxt_gamma.append(gm.CF(node["orig_name"], node["obs_val"], int_vars, int_values))
            nxt = cf_ID(g, nxt_gamma, v)
            product_list.append(deepcopy(nxt.p))
            id_check_list.append(deepcopy(nxt.tree.call.id_check))
            tree.children.append(deepcopy(nxt.tree))
        tree.call.id_check = all(id_check_list)

        # Outer sum
        obs_nodes = cg.vs.select(description=None)["name"]
        nodes_to_remove = []
        for event in gamma_prime:
            nodes_to_remove.append(f"{event.orig_name}_{event.int_vars}")
        summation_set = list(set(obs_nodes)-set(nodes_to_remove))
        return gm.CfResultsInternal(p=gm.Probability(sumset=summation_set, product=True, children=product_list),
                                    tree=tree)

    # Line 7
    else:
        s_single = s[0]

        # Line 8
        sub = []
        ev = []
        for node in s_single:
            for int_val in node["int_values"]:
                sub.append(int_val)
            ev.append(node["obs_val"])
        if len(set(sub)-set(ev)) != 0:
            tree.call.line = 8
            tree.call.id_check = False
            return gm.CfResultsInternal(tree=tree, p_message="counterfactual contains an inconsistent value assignment")

        # Line 9
        else:
            tree.call.line = 9
            tree.call.id_check = True
            new_x = []
            var = []
            for node in s_single:
                for int_var in node["int_vars"]:
                    new_x.append(int_var)
                var.append(node["orig_name"])
            return gm.CfResultsInternal(gm.Probability(var=var, subscript=new_x), tree)


def cf_IDC(g, gamma, delta, tree=gm.CfTreeNode()):  # todo: document that line numbers have 10 added
    g_obs = gm.observed_graph(g)
    topo_ind = g_obs.topological_sorting()
    topo = gm.to_names(topo_ind, g_obs)
    tree.call = gm.CfCall(gamma=gamma, delta=delta, g=g, line=10, id_check=False)
    for cf in gamma:
        cf.cond = "gamma"
    for cf in delta:
        cf.cond = "delta"

    # Line 1
    if cf_ID(g, delta, topo).p_int == 0:
        tree.call.line = 11
        tree.call.id_check = False
        return gm.CfResultsInternal(tree=tree, p_message="Undefined: delta is inconsistent")

    # Line 2
    (g_prime, cf_conj_prime) = gm.make_cg(g, gamma+delta)

    # Line 3
    if cf_conj_prime == "Inconsistent":
        tree.call.line = 13
        tree.call.id_check = True
        return gm.CfResultsInternal(tree=tree, p_int=0, p_message="Counterfactual is Inconsistent")

    # Line 4
    gamma_prime_names = []
    gamma_prime = []
    delta_prime = []
    for cf in cf_conj_prime:
        if cf.cond == "gamma":
            gamma_prime_names.append(f"{cf.orig_name}_{cf.int_vars}")
            gamma_prime.append(cf)
        else:
            delta_prime.append(cf)

    for cf in delta_prime:
        node = f"{cf.orig_name}_{cf.int_vars}"
        g_prime_y = deepcopy(g_prime)
        edges = set(g_prime.es.select().indices) - set(g_prime.es.select(_from_in=g.vs.select(name=node).indices).indices)
        g_prime_y = g_prime_y.subgraph_edges(edges, delete_vertices=False)

        if gm.wrap_d_sep(g_prime_y, [node], gamma_prime_names):
            gamma_prime_y = []
            for gamma_cf in gamma_prime:
                gamma_name = f"{gamma_cf.original_name}_{gamma_cf.int_vars}"
                if gamma_name in gm.find_related_nodes_of([gamma_name], g_prime, mode="in", order="max"):
                    new_cf = deepcopy(gamma_cf)
                    new_cf.int_vars.append(cf.orig_name)
                    new_cf.int_values.append(cf.obs_val)
                    gamma_prime_y.append(new_cf)
            delta_prime.remove(cf)

            tree.call.line = 14
            nxt = cf_IDC(g, gamma_prime_y, delta_prime)
            tree.children.append(deepcopy(nxt.tree))
            tree.call.id_check = nxt.tree.call.id_check
            return gm.CfResultsInternal(nxt.p, tree, nxt.p_int, nxt.p_message)

    # Line 5
    tree.call.line = 15
    num = cf_ID(g, cf_conj_prime, topo)
    delta_names = []
    for cf in delta:
        delta_names.append(f"{cf.original_name}_{cf.int_vars}")
    tree.children.append(deepcopy(num.tree))
    tree.call.id_check = num.tree.call.id_check
    return gm.CfResultsInternal(gm.Probability(cf_p_prime=num.p, cf_delta=delta_names), tree, num.p_int, num.p_message)