import pytest
import igraph
import automates.model_analysis.graph_manipulation as gm
from automates.model_analysis.identification_algorithms import identifiability


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