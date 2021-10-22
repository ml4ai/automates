import pytest
import igraph
import automates.model_analysis.graph_manipulation as gm
from automates.model_analysis.identification_algorithms import identifiability, cf_identifiability


def test_identifiability():
    """
    Graph 3A from Shpitzer and Pearl 2006.
    Tests summation notation, product notation
    :return:
    """
    g = igraph.Graph(edges=[[0, 1], [1, 2], [3, 4], [0, 2], [0, 4], [0, 3], [1, 3], [2, 0], [4, 0], \
                            [3, 0], [3, 1]], directed=True)
    g.vs["name"] = ["W1", "X", "Y1", "W2", "Y2"]
    g.es["description"] = ["O", "O", "O", "U", "U", "U", "U", "U", "U", "U", "U"]
    y = ["Y1", "Y2"]
    x = ["X"]
    results = identifiability(y, x, g, steps=True)
    assert results.p == "\\sum_{W2}\\left(\\sum_{W1}P(Y1|W1,X)P(W1),\\right)P(Y2|W2)P(W2)"


def test_non_identifiability():
    """
    Graph 3B from Shpitzer and Pearl 2006.
    Not identifiable, tests line 2 code
    :return:
    """
    g = igraph.Graph(edges=[[0, 1], [1, 2], [3, 4], [0, 2], [0, 4], [0, 3], [1, 3], [2, 0], [4, 0], \
                            [3, 0], [3, 1], [0, 3]], directed=True)
    g.vs["name"] = ["W1", "X", "Y1", "W2", "Y2"]
    g.es["description"] = ["O", "O", "O", "U", "U", "U", "U", "U", "U", "U", "U", "O"]
    y = ["Y1", "Y2"]
    x = ["X"]
    with pytest.raises(gm.IDANotIdentifiable):
        identifiability(y, x, g)


def test_conditional_identifiability():
    g = igraph.Graph(edges=[[0, 1], [1, 2], [0, 1], [1, 0]], directed=True)
    g.vs["name"] = ["X", "Z", "Y"]
    g.es["description"] = ["O", "O", "U", "U"]
    y = ["Y"]
    x = ["X"]
    z = ["Z"]
    results = identifiability(y, x, g, z)
    assert results == "\\frac{P(Y|X,Z)}{\\sum_{Y}P(Y|X,Z)}"


def test_conditional_non_identifiability():
    g = igraph.Graph(edges=[[0, 1], [2, 1], [0, 1], [1, 0]], directed=True)
    g.vs["name"] = ["X", "Z", "Y"]
    g.es["description"] = ["O", "O", "U", "U"]
    y = ["Y"]
    x = ["X"]
    z = ["Z"]
    with pytest.raises(gm.IDANotIdentifiable):
        identifiability(y, x, g, z)
        
        
def test_d_sep_true():
    g = igraph.Graph(edges=[[0, 2], [1, 2], [2, 3], [2, 4], [3, 5], [5, 6]], directed=True)
    g.vs["name"] = ["A", "B", "C", "D", "E", "F", "G"]
    assert gm.d_sep(g, ["D"], ["E"], ["C"])
    
    
def test_d_sep_false():
    g = igraph.Graph(edges=[[0, 2], [1, 2], [2, 3], [2, 4], [3, 5], [5, 6]], directed=True)
    g.vs["name"] = ["A", "B", "C", "D", "E", "F", "G"]
    assert not gm.d_sep(g, ["A"], ["B"], ["D", "F"])


def test_make_cg():
    # Setup
    gamma = [gm.CF("Y", "y", ["X"], ["x"]), gm.CF("X", "x_prime"), gm.CF("Z", "z", ["D"], ["d"]), gm.CF("D", "d")]
    g = igraph.Graph(edges=[[0, 1], [1, 2], [3, 4], [4, 2], [0, 2], [2, 0]], directed=True)
    g.vs["name"] = ["X", "W", "Y", "D", "Z"]
    g.es["description"] = ["O", "O", "O", "O", "U", "U"]

    # Function Results
    (cg, gamma_prime) = gm.make_cg(g, gamma)

    # Expected Results
    cg_exp = igraph.Graph(edges=[[1, 2], [4, 5], [3, 4], [6, 0], [6, 5], [2, 5]], directed=True)
    cg_exp.vs["name"] = ['X', 'D', 'Z', 'X_[X]', 'W_[X]', 'Y_[X]', 'U_1']
    cg_exp.es["description"] = ["O", "O", "O", "U", "U", "O"]
    gamma_prime_exp = [gm.CF('Y', 'y', ['X'], ['x']), gm.CF('X', 'x_prime'), gm.CF('Z'), gm.CF('D', 'd')]

    assert cg.isomorphic(cg_exp) and (gamma_prime == gamma_prime_exp)


def test_make_cg_multi_intervention():
    # Setup
    gamma = [gm.CF("Y", "y", ["X", "Z"], ["x", "z"]), gm.CF("X", "x_prime")]
    g = igraph.Graph(edges=[[0, 1], [1, 2], [3, 4], [4, 2], [0, 2], [2, 0]], directed=True)
    g.vs["name"] = ["X", "W", "Y", "D", "Z"]
    g.es["description"] = ["O", "O", "O", "O", "U", "U"]

    # Function Results
    (cg, gamma_prime) = gm.make_cg(g, gamma)

    # Expected Results
    cg_exp = igraph.Graph(edges=[[2, 3], [4, 3], [1, 2], [5, 0], [5, 3]], directed=True)
    cg_exp.vs["name"] = ['X', "X_['X', 'Z']", "W_['X', 'Z']", "Y_['X', 'Z']", "Z_['X', 'Z']", 'U_1']
    cg_exp.es["description"] = ["O", "O", "O", "U", "U"]
    gamma_prime_exp = [gm.CF("Y", "y", ["X", "Z"], ["x", "z"]), gm.CF("X", "x_prime")]

    assert cg.isomorphic(cg_exp) and (gamma_prime == gamma_prime_exp)


def test_cf_identifiability():
    # Setup
    gamma = [gm.CF("Y", "y", ["X"], ["x"])]
    delta = [gm.CF("X", "x_prime"), gm.CF("Z", "z", ["D"], ["d"]), gm.CF("D", "d")]
    g = igraph.Graph(edges=[[0, 1], [1, 2], [3, 4], [4, 2], [0, 2], [2, 0]], directed=True)
    g.vs["name"] = ["X", "W", "Y", "D", "Z"]
    g.es["description"] = ["O", "O", "O", "O", "U", "U"]

    # Function Results
    results = cf_identifiability(g, gamma, delta)

    # Expected Results
    exp = "P'/P'(x_prime), where P' = \\sum_{W_['X', 'Z'],X}P_{Z,W}(x_prime,y)P_{X}(W)"
    assert(results == exp)
