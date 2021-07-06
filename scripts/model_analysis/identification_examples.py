from automates.model_analysis.graph_manipulation import *

gamma = [CF("Y", "y", "X"), CF("X", "x_prime"), CF("Z", "z", "D"), CF("D", "d")]
graph_9a = igraph.Graph(edges=[[0, 1], [1, 2], [3, 4], [4, 2], [0, 2], [2, 0]], directed=True)
graph_9a.vs["name"] = ["X", "W", "Y", "D", "Z"]
# graph_9a.vs["orig_name"] = ["X", "W", "Y", "D", "Z"]
# graph_9a.vs["val_assign"] = ["x_prime", None, None, "d", None]
# graph_9a.vs["int_var"] = [None, "X", "X", None, "X"]
graph_9a.es["description"] = ["O", "O", "O", "O", "U", "U"]
cg = make_cg(graph_9a, gamma)
print(cg)