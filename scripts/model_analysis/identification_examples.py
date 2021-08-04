import automates.model_analysis.graph_manipulation as gm
import automates.model_analysis.identification_algorithms as ia
import igraph
import copy

gamma = [gm.CF("Y", "y", ["X"], ["x"]), gm.CF("X", "x_prime"), gm.CF("Z", "z", ["D"], ["d"]), gm.CF("D", "d")]
graph_9a = igraph.Graph(edges=[[0, 1], [1, 2], [3, 4], [4, 2], [0, 2], [2, 0]], directed=True)
graph_9a.vs["name"] = ["X", "W", "Y", "D", "Z"]
graph_9a.es["description"] = ["O", "O", "O", "O", "U", "U"]
# (cg, gamma_prime) = gm.make_cg(graph_9a, gamma)
# print(cg)
# print(gamma_prime)
#
# cg_exp = igraph.Graph(edges=[[1, 2], [4, 5], [3, 4], [6, 0], [6, 5], [2, 5]], directed=True)
# print(cg.isomorphic(cg_exp))

gamma2 = [gm.CF("Y", "y", ["X", "Z"], ["x", "z"]), gm.CF("X", "x_prime")]
(cg2, gamma_prime2) = gm.make_cg(graph_9a, gamma2)
print(cg2)
print(cg2.vs["name"])
print(cg2.vs.indices)
print(gamma_prime2)
