import sys

import numpy as np
import networkx as nx


def main():
    # Loading the two trees:
    treefile1 = "/Users/paulh/Google Drive/ASKE-AutoMATES/Data/MESA/simple_example_trees/tree1.dot"
    treefile2 = "/Users/paulh/Google Drive/ASKE-AutoMATES/Data/MESA/simple_example_trees/tree2.dot"

    T1 = nx.DiGraph(nx.drawing.nx_pydot.read_dot(treefile1))
    T2 = nx.DiGraph(nx.drawing.nx_pydot.read_dot(treefile2))

    # Preprocessing :
    T1_pstorder_nodes = list(nx.dfs_postorder_nodes(T1))
    T2_pstorder_nodes = list(nx.dfs_postorder_nodes(T2))

    print(T1_pstorder_nodes, T2_pstorder_nodes)
    print(
        leftmost_descendants(T1, T1_pstorder_nodes),
        leftmost_descendants(T2, T2_pstorder_nodes),
    )
    sys.exit()

    # label nodes <-> Index of left1/left2 and keyroots1/keyroots2 arrays
    # position = [0, 1, 2, 3, 4, 5, 6]

    # Left most descendants of each tree
    # L1 = [None, 1, 1, 3, 4, 1, 1]
    # L2 = [None, 1, 1, 3, 3, 5, 1]

    # keyroots are functions that take the trees as inputs and generate the keyroots
    K1 = [None, 0, 0, 1, 1, 0, 1]
    K2 = [None, 0, 0, 0, 1, 1, 1]

    distance_tables = root_compare(K1, K2, L1, L2)
    print(distance_tables)


def cost(a, b):
    return 0 if a == b else 1


def leftmost_descendants(T: nx.DiGraph, nodes: list) -> list:
    """Returns a list of the leftmost nodes for each node in nodes, where nodes
    is a post-order list of all nodes in the tree T.
    """
    result = []
    for node in nodes:
        succs = list(T.successors(node))
        while len(succs) > 0:
            node = succs[0]
            succs = list(T.successors(node))
        result.append(node)
    return result


def root_compare(kroots1, kroots2, lefts1, lefts2):
    results = [[None for j in range(kroots2)] for i in range(kroots1)]
    for k1, root1 in enumerate(kroots1):
        for k2, root2 in enumerate(kroots2):
            _, tdist = treedist(root1, root2, lefts1, lefts2)
            results[k1][k2] = tdist
    return results


def treedist(pos1, pos2, lefts1, lefts2):
    bound1 = pos1 - lefts1[pos1] + 2
    bound2 = pos2 - lefts2[pos2] + 2

    fdist = np.zeros((bound1, bound2))
    tdist = np.zeros((bound1, bound2))

    # fdist[0][0] = 0
    for i in range(0, bound1):
        fdist[i][0] = fdist[i - 1][0] + c[1][0]
    for i in range(0, bound2):
        fdist[0][i] = fdist[0][i - 1] + c[0][1]

    for k in range(lefts1[pos1], pos1, -1):
        for i in range(1, k):
            for l in range(lefts2[pos2], pos2, -1):
                for j in range(0, l):
                    if lefts1[k] == lefts1[pos1] and lefts2[l] == lefts2[pos2]:
                        fdist[i][j] = min(
                            fdist[i - 1][j] + c[0][l],
                            fdist[i][j - 1] + c[k][0],
                            fdist[i - 1][j - 1] + c[k][l],
                        )

                tdist[k][l] = fdist[i][j]
            else:
                m = lefts1[k] - lefts1[pos1]
                n = lefts2[l] - lefts2[pos2]
                fdist[i][j] = min(
                    fdist[i - 1][j] + c[0][l],
                    fdist[i][j - 1] + c[k][0],
                    fdist[i - 1][j - 1] + tdist[k][l],
                )

    return fdist, tdist


if __name__ == "__main__":
    main()
