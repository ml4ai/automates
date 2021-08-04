import automates.model_analysis.graph_manipulation as gm
import automates.model_analysis.identification_algorithms as ia
import igraph
import copy

gamma = [gm.CF("Y", "y", ["X"], ["x"]), gm.CF("X", "x_prime"), gm.CF("Z", "z", ["D"], ["d"]), gm.CF("D", "d")]
graph_9a = igraph.Graph(edges=[[0, 1], [1, 2], [3, 4], [4, 2], [0, 2], [2, 0]], directed=True)
graph_9a.vs["name"] = ["X", "W", "Y", "D", "Z"]
graph_9a.es["description"] = ["O", "O", "O", "O", "U", "U"]
(cg, gamma_prime) = gm.make_cg(graph_9a, gamma)
# print(cg)
# print(gamma_prime)


