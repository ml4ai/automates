import automates.model_analysis.graph_manipulation as gm
import igraph

# todo: Determine if obs_val is necessary for "Y" and "Z"
gamma = [gm.CF("Y", "y", "X", "x"), gm.CF("X", "x_prime"), gm.CF("Z", "z", "D", "d"), gm.CF("D", "d")]
graph_9a = igraph.Graph(edges=[[0, 1], [1, 2], [3, 4], [4, 2], [0, 2], [2, 0]], directed=True)
graph_9a.vs["name"] = ["X", "W", "Y", "D", "Z"]
# graph_9a.vs["orig_name"] = ["X", "W", "Y", "D", "Z"]
# graph_9a.vs["obs_val"] = ["x_prime", None, None, "d", None]
# graph_9a.vs["int_var"] = [None, "X", "X", None, "X"]
graph_9a.es["description"] = ["O", "O", "O", "O", "U", "U"]
cg = gm.parallel_worlds(graph_9a, gamma)
print(cg)
print(cg.vs()["name"])
print(cg.vs()["orig_name"])
print(cg.vs()["obs_val"])
print(cg.vs()["int_var"])
print(cg.vs()["int_value"])


# mit_dsep_ex = igraph.Graph(edges=[[0, 2], [1, 2], [2, 3], [2, 4], [3, 5], [5, 6]], directed=True)
# mit_dsep_ex.vs["name"] = ["A", "B", "C", "D", "E", "F", "G"]
# print(gm.d_sep(mit_dsep_ex, ["A"], ["B"], ["D", "F"]))
# print(gm.d_sep(mit_dsep_ex, ["D"], ["E"], ["C"]))

# ch = gm.children_unsort(["Z"], graph_9a)
# vert = graph_9a.vs.select(name=ch[0])
# print(vert["orig_name"])
