import numpy
import igraph
import automates.model_analysis.graph_manipulation as gm
import automates.model_analysis.identification_algorithms as ia


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
        res = ia.compute_ID(y, x, gm.Probability(), g, g_obs, topo, topo, [])
        algo = "id"
        res_prob = res.p
    else:
        res = ia.compute_IDC(y, x, z, gm.Probability(), g, g_obs, topo, topo, [])  # todo: write this
        algo = "idc"
        res_num = res.p
        res_den = res.p
        res_den.sumset = list(set(y) | set(res_den.sumset))
        res_prob = gm.Probability(fraction=True, num=res_num, den=res_den)
    res_tree = res.tree
    if res.tree.call.id_check:
        output = gm.Results(query={"y": y, "x": x, "z": z}, algorithm=algo, p=gm.get_expression(res_prob), tree=res_tree)
        if steps:
            return output
        return output.p
    else:
        if stop_on_noid:
            raise Exception("Not Identifiable")
        output = gm.Results(query={"y": y, "x": x, "z": z}, algorithm=algo, p="", tree=res_tree)
        if steps:
            return output
        return output.p
