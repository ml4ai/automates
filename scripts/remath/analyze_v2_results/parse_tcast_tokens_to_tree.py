from typing import List, Dict
from dataclasses import dataclass, field
import os
import pprint
import difflib
import networkx
from analyze_results import load_v2_results_data


@dataclass
class TCAST:
    tokens: List[str] = None
    vars: Dict[str, str] = field(default_factory=dict)
    vals: Dict[str, str] = field(default_factory=dict)


def tcast_to_tree(tcast: TCAST):
    G = networkx.DiGraph()
    node_counter = 0
    node_stack = list()
    next_head = False
    for elm in tcast.tokens:
        if elm == '(':
            next_head = True
        elif elm == ')':
            if len(node_stack) > 1:
                G.add_edge(node_stack[-2], node_stack[-1])
            node_stack.pop()
        elif next_head:
            node_stack.append(f'{node_counter}@{elm}')
            node_counter += 1
            next_head = False
        elif elm.startswith('Var'):
            if elm in tcast.vars:
                var_str = f'{node_counter}@{elm}={tcast.vars[elm]}'
            else:
                var_str = f'{node_counter}@{elm}'
            node_counter += 1
            G.add_edge(node_stack[-1], var_str)
        elif elm.startswith('Val'):
            if elm in tcast.vals:
                val_str = f'{node_counter}@{elm}={tcast.vals[elm]}'
            else:
                val_str = f'{node_counter}@{elm}'
            node_counter += 1
            G.add_edge(node_stack[-1], val_str)
    return G


def parse_tcast_file(filepath):
    tcast = TCAST()
    in_vars_p = False
    in_vals_p = False
    with open(filepath, 'r') as tcast_file:
        for line in tcast_file.readlines():
            if tcast.tokens is None:
                tcast.tokens = line.strip('\n ').split(' ')
            elif line.startswith('--------- VARIABLES ---------'):
                in_vars_p = True
            elif line.startswith('--------- VALUES ---------'):
                in_vars_p = False
                in_vals_p = True
            elif in_vars_p:
                tcast.vars[f'Var{len(tcast.vars)}'] = line.strip('\n ')
            elif in_vals_p:
                tcast.vals[f'Val{len(tcast.vals)}'] = line.strip(' \n').replace(':', '>').replace('\\n', '')
    return tcast


def save_graph_dot(G, filepath):
    # labels = {1: 'root', 2: 'child1', 3: 'child2'}
    # G = networkx.Graph()
    # G.add_nodes_from(['1_main', '2_child1', '3_child2'])
    # G.add_edges_from([('1_main', '2_child1'), ('1_main', '3_child2')])
    # networkx.draw(G, labels=labels, with_labels=True)
    networkx.drawing.nx_pydot.write_dot(G, filepath)


def parse_and_save_tcast_dot(filepath):
    tcast = parse_tcast_file(filepath)
    # pprint.pprint(tcast)
    G = tcast_to_tree(tcast)
    dot_filepath = filepath.split(os.sep)[-1].split('--')[0] + '--tCAST.dot'
    save_graph_dot(G, dot_filepath)


def difflib_example():
    cases = [(('a', 'b', 'c'), ('a', 'b', 'd'))]
    for a, b in cases:
        print(f'{a} => {b}')
        for i, s in enumerate(difflib.ndiff(a, b)):
            if s[0] == ' ': continue
            elif s[0] == '-':
                print(f'Delete {s[-1]} from position {i}: {s}')
            elif s[0] == '+':
                print(f'Add {s[-1]} to position {i}: {s}')
        print()


def diff_tcast(tcast_target, tcast_predicted, name):
    print('target:')
    print(tcast_target)
    print('predicted:')
    print(tcast_predicted)
    print('diff:')

    G = tcast_to_tree(TCAST(tokens=tcast_target[1:-1]))
    save_graph_dot(G, name + '--tCAST.dot')

    # d = 0
    for i, s in enumerate(difflib.ndiff(tcast_target, tcast_predicted)):
        if s[0] == ' ': continue
        elif s[0] == '-':
            print(f'Delete {s.split(" ")[-1]} from position {i}: {s}')
            # print(f'    targ: {tcast_target[i + d]}')
            # print(f'    pred: {tcast_predicted[i - d]}')
            # d -= 1
        elif s[0] == '+':
            print(f'Add {s.split(" ")[-1]} to position {i}: {s}')
            # print(f'    targ: {tcast_target[i + d]}')
            # print(f'    pred: {tcast_predicted[i - d]}')
            # d += 1


def diff_tcast_for(data, name):
    score, target, predicted = data[name]
    print(f'Diff for {name}: {score}')
    diff_tcast(target, predicted, name)
    print()


def main():
    difflib_example()

    # parse_and_save_tcast_dot('../corpus_8400_8599/tokens_output/expr_v2_0008400--CAST.tcast')

    bleu_data = load_v2_results_data('test_bleu')

    print('\n ----- SUCCEEDED')
    diff_tcast_for(bleu_data, 'expr_v2_0244711')

    print('\n ----- FAILED')
    diff_tcast_for(bleu_data, 'expr_v2_0240401')

    print('\n ----- Score 0.9')
    diff_tcast_for(bleu_data, 'expr_v2_0241483')

    print('\n ----- Score 0.8')
    diff_tcast_for(bleu_data, 'expr_v2_0242189')

    print('\n ----- Score 0.6')
    diff_tcast_for(bleu_data, 'expr_v2_0238355')

    print('DONE')


if __name__ == '__main__':
    main()

