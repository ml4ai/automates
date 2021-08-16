import automates.model_analysis.graph_manipulation as gm
import automates.model_analysis.identification_algorithms as ia
import matplotlib.pyplot as plt
import igraph

# model 1: Simple_SIR
simple_sir_edges = [[0, 6], [0, 8], [1, 6], [1, 7], [1, 9], [2, 6], [2, 10], [3, 6], [4, 7], [5, 6], [5, 7],
                    [6, 8], [6, 9], [7, 9], [7, 10]]
simple_sir_names = ['s', 'i', 'r', 'beta', 'gamma', 'dt', 'inf', 'rec', 's2', 'i2', 'r2']
simple_sir = igraph.Graph(edges=simple_sir_edges, directed=True)
simple_sir.vs["name"] = simple_sir_names

visual_style_simple_sir = {"vertex_label": simple_sir.vs["name"], "vertex_size": 10}

# Following Line of code is an optional graph layout. It may be helpful, but is harder to read
# visual_style_simple_sir["layout"] = simple_sir.layout("rt", mode="all", root=[0, 1, 2])
fig, ax = plt.subplots()
igraph.plot(simple_sir, target=ax, **visual_style_simple_sir)
# plt.show()

# model 2: CHIME_SIR (v01)
chime_sir_edges = [[0, 5], [0, 6], [1, 5], [1, 6], [1, 7], [2, 7], [3, 5], [3, 6], [4, 6], [4, 7], [5, 9],
                   [5, 10], [6, 9], [6, 11], [7, 9], [7, 12], [8, 9], [9, 10], [9, 11], [9, 12]]
chime_sir_names = ['s', 'i', 'r', 'beta', 'gamma', 's_n', 'i_n', 'r_n', 'n', 'scale', 's1', 'i2', 'r2']
chime_sir = igraph.Graph(edges=chime_sir_edges, directed=True)
chime_sir.vs["name"] = chime_sir_names

visual_style_chime_sir = {"vertex_label": chime_sir.vs["name"], "vertex_size": 10}
fig, ax = plt.subplots()
igraph.plot(chime_sir, target=ax, **visual_style_chime_sir)
# plt.show()

Y = ["s2", "i2", "r2"]
X = ["s"]
Z = ["i", "r"]
# p = ia.identifiability(y=Y, x=X, z=Z, g=simple_sir)


# For spot-checking cf_identifiability
gamma = [gm.CF("Y", "y", ["X"], ["x"]), gm.CF("X", "x_prime"), gm.CF("Z", "z", ["D"], ["d"]), gm.CF("D", "d")]
g = igraph.Graph(edges=[[0, 1], [1, 2], [3, 4], [4, 2], [0, 2], [2, 0]], directed=True)
g.vs["name"] = ["X", "W", "Y", "D", "Z"]
g.es["description"] = ["O", "O", "O", "O", "U", "U"]
ia.cf_identifiability(g, gamma)

