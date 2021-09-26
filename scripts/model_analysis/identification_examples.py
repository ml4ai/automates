import automates.model_analysis.graph_manipulation as gm
import igraph

gamma = [gm.CF("Y", "y", "X"), gm.CF("X", "x_prime"), gm.CF("Z", "z", "D"), gm.CF("D", "d")]
graph_9a = igraph.Graph(edges=[[0, 1], [1, 2], [3, 4], [4, 2], [0, 2], [2, 0]], directed=True)
graph_9a.vs["name"] = ["X", "W", "Y", "D", "Z"]
# graph_9a.vs["orig_name"] = ["X", "W", "Y", "D", "Z"]
# graph_9a.vs["val_assign"] = ["x_prime", None, None, "d", None]
# graph_9a.vs["int_var"] = [None, "X", "X", None, "X"]
graph_9a.es["description"] = ["O", "O", "O", "O", "U", "U"]
cg = gm.make_cg(graph_9a, gamma)
# print(cg)


mit_dsep_ex = igraph.Graph(edges=[[0, 2], [1, 2], [2, 3], [2, 4], [3, 5], [5, 6]], directed=True)
mit_dsep_ex.vs["name"] = ["A", "B", "C", "D", "E", "F", "G"]
print(gm.d_sep(mit_dsep_ex, ["A"], ["B"], ["D", "F"]))
print(gm.d_sep(mit_dsep_ex, ["D"], ["E"], ["C"]))
