import networkx as nx

'''
G.add_edges_from(
  [
    ("=", "/"),
    ("=", "\delta")
  ]
)
G.add_node('my_plus1', label="+")
G.add_node('my_plus2', label="+")
G.add_edge('my_plus1', "T")
G.add_edge('my_plus2', "237.3")
G.add_edge('-', 'my_plus1')
G.add_edge('-', 'my_plus2')
'''


def gen_mesa_MITRE_code_1():
    print('gen_mesa_MITRE_code_1(): ', end='')

    G = nx.DiGraph()

    G.add_node('m1', label="*")
    G.add_node('n1', label="-1")
    G.add_node('s1', label="S")

    G.add_node('m2', label="*")
    G.add_node('n2', label="-1")
    G.add_node('s2', label="S")

    G.add_node('m3', label="*")
    G.add_node('n3', label="-1")
    G.add_node('s3', label="S")

    G.add_node('m4', label="*")
    G.add_node('n4', label="-1")
    G.add_node('s4', label="S")

    G.add_edge('=', 'dS_dt')
    G.add_edge('=', '+')

    G.add_edge('+', 'm1')
    G.add_edge('+', 'm2')
    G.add_edge('+', 'm3')
    G.add_edge('+', 'm4')

    G.add_edge('m1', 'n1')
    G.add_edge('m1', 'b0')
    G.add_edge('m1', 'I0')
    G.add_edge('m1', 's1')

    G.add_edge('m2', 'n2')
    G.add_edge('m2', 'b1')
    G.add_edge('m2', 'I1')
    G.add_edge('m2', 's2')

    G.add_edge('m3', 'n3')
    G.add_edge('m3', 'b2')
    G.add_edge('m3', 'I2')
    G.add_edge('m3', 's3')

    G.add_edge('m4', 'n4')
    G.add_edge('m4', 'b3')
    G.add_edge('m4', 'I3')
    G.add_edge('m4', 's4')

    A = nx.nx_agraph.to_agraph(G)
    # NOTE: Pygraphviz and graphviz are needed to do the drawing in this step
    A.draw("mesa_tree_example_MITRE_code_1.pdf", prog="dot")

    print('DONE')


def gen_mesa_MITRE_eq_1():
    print('gen_mesa_MITRE_eq_1(): ', end='')

    G = nx.DiGraph()

    G.add_node('m1', label="*")
    G.add_node('n1', label="$-1$")
    G.add_node('s1', label="$S$")

    G.add_node('m2', label="*")
    G.add_node('n2', label=r"$-1$")
    G.add_node('s2', label=r"$S$")

    G.add_node('m3', label="*")
    G.add_node('n3', label="$-1$")
    G.add_node('s3', label="$S$")

    G.add_node('m4', label="*")
    G.add_node('n4', label="$-1$")
    G.add_node('s4', label="$S$")

    G.add_edge('=', r'$$\dot{S}$$')
    G.add_edge('=', '+')

    G.add_edge('+', 'm1')
    G.add_edge('+', 'm2')
    G.add_edge('+', 'm3')
    G.add_edge('+', 'm4')

    G.add_edge('m1', 'n1')
    G.add_edge('m1', '$\beta_0$')
    G.add_edge('m1', '$I_0$')
    G.add_edge('m1', 's1')

    G.add_edge('m2', 'n2')
    G.add_edge('m2', '$\beta_1$')
    G.add_edge('m2', '$I_1$')
    G.add_edge('m2', 's2')

    G.add_edge('m3', 'n3')
    G.add_edge('m3', '$\beta_2$')
    G.add_edge('m3', '$I_2$')
    G.add_edge('m3', 's3')

    G.add_edge('m4', 'n4')
    G.add_edge('m4', '$\beta_3$')
    G.add_edge('m4', '$I_3$')
    G.add_edge('m4', 's4')

    A = nx.nx_agraph.to_agraph(G)
    # NOTE: Pygraphviz and graphviz are needed to do the drawing in this step
    A.draw("mesa_tree_example_MITRE_eq_1.pdf", prog="dot")

    print('DONE')


if __name__ == '__main__':
    gen_mesa_MITRE_code_1()
    gen_mesa_MITRE_eq_1()
