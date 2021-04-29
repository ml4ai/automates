import pytest
import igraph
from automates.model_analysis.identification_algorithms import identifiability


def test_identifiability():
    g = igraph.Graph(edges=[[0, 1], [1, 2], [3, 4], [0, 2], [0, 4], [0, 3], [1, 3], [2, 0], [4, 0], \
                             [3, 0], [3, 1]], directed=True)
    g.vs["name"] = ["W1", "X", "Y1", "W2", "Y2"]
    g.es["description"] = ["O", "O", "O", "U", "U", "U", "U", "U", "U", "U", "U"]
    y = ["Y1", "Y2"]
    x = ["X"]
    results = identifiability(y, x, g, steps=True)
    assert results.p == "\\sum_{W2}\\left(\\sum_{W1}P(Y1|W1,X)P(W1),\\right)P(Y2|W2)P(W2)"


def test_non_identifiability():
    g = igraph.Graph(edges=[[0, 1], [1, 2], [3, 4], [0, 2], [0, 4], [0, 3], [1, 3], [2, 0], [4, 0], \
                          [3, 0], [3, 1], [0, 3]], directed=True)
    g.vs["name"] = ["W1", "X", "Y1", "W2", "Y2"]
    g.es["description"] = ["O", "O", "O", "U", "U", "U", "U", "U", "U", "U", "U", "O"]
    y = ["Y1", "Y2"]
    x = ["X"]
    with pytest.raises(Exception):
        identifiability(y, x, g)
