from copy import deepcopy

from networkx.algorithms.simple_paths import all_simple_paths
from automates.model_assembly.networks import (
    GrFNLoopSubgraph,
    GrFNSubgraph,
    GroundedFunctionNetwork,
    HyperEdge,
    LambdaNode,
)
from automates.model_assembly.structures import LambdaType


def remove_node_and_hyper_edges(grfn: GroundedFunctionNetwork, node):
    for grfn_node in grfn.nodes:
        if node.uid == grfn_node.uid:
            grfn.remove_node(grfn_node)
            break

    def remove_from_subgraphs(g):
        if node in g.nodes:
            g.nodes = [n for n in g.nodes if n != node]
        for sub in grfn.subgraphs.successors(g):
            remove_from_subgraphs(sub)

    remove_from_subgraphs(grfn.root_subgraph)

    edges_to_remove = set()
    for hyper_edge in grfn.hyper_edges:
        if node in hyper_edge.inputs:
            hyper_edge.inputs.remove(node)
            if len(hyper_edge.inputs) == 0:
                edges_to_remove.add(hyper_edge)
        elif node in hyper_edge.outputs:
            hyper_edge.outputs.remove(node)
            if len(hyper_edge.outputs) == 0:
                edges_to_remove.add(hyper_edge)
        elif node == hyper_edge.lambda_fn:
            edges_to_remove.add(hyper_edge)

    grfn.hyper_edges = [h for h in grfn.hyper_edges if h not in edges_to_remove]
    for edge in edges_to_remove:
        grfn.lambdas = [l for l in grfn.lambdas if edge.lambda_fn.uid != l.uid]


def get_input_interface_node(grfn: GroundedFunctionNetwork, subgraph: GrFNSubgraph):
    return [
        node
        for node in subgraph.nodes
        if isinstance(node, LambdaNode)
        and node.func_type == LambdaType.INTERFACE
        and all([node_succ in subgraph.nodes for node_succ in grfn.successors(node)])
    ][0]


def get_output_interface_node(grfn: GroundedFunctionNetwork, subgraph: GrFNSubgraph):
    return [
        node
        for node in subgraph.nodes
        if isinstance(node, LambdaNode)
        and node.func_type == LambdaType.INTERFACE
        and all([node_succ in subgraph.nodes for node_succ in grfn.predecessors(node)])
    ][0]


def get_decision_nodes(subgraph: GrFNSubgraph):
    return [
        node
        for node in subgraph.nodes
        if isinstance(node, LambdaNode) and node.func_type == LambdaType.DECISION
    ]


def extract_dynamics_from_loop(grfn: GroundedFunctionNetwork, loop: GrFNLoopSubgraph):
    # Create a copy of the current grfn to trim nodes out of to create the
    # model dynamics grfn
    dynamics_grfn = deepcopy(grfn)
    dynamics_grfn_subgraphs_graph = dynamics_grfn.subgraphs
    loop_copy = [s for s in dynamics_grfn.subgraphs if s == loop][0]
    to_remove = set()

    # Delete all other loop subgraphs besides the loop we are operating on from
    # the root subgraph. TODO test if this works
    loop_subgraphs_to_remove = []
    for subgraph in dynamics_grfn_subgraphs_graph.successors(
        dynamics_grfn.root_subgraph
    ):
        if subgraph != loop and isinstance(subgraph, GrFNLoopSubgraph):
            loop_subgraphs_to_remove.append(subgraph)
    for subgraph in loop_subgraphs_to_remove:
        dynamics_grfn_subgraphs_graph.remove_node(subgraph)

    # Generatate the input/output var pairs for the loop interface
    loop_successors = dynamics_grfn_subgraphs_graph.successors(loop)
    loop_interface = get_input_interface_node(dynamics_grfn, loop)
    loop_output_interface = get_output_interface_node(dynamics_grfn, loop)
    loop_decisions = get_decision_nodes(loop)

    loop_interface_hyper_edge = [
        h for h in grfn.hyper_edges if h.lambda_fn == loop_interface
    ][0]
    loop_interfaces_input_output_var_pairs = []
    for (input, output) in zip(
        loop_interface_hyper_edge.inputs, loop_interface_hyper_edge.outputs
    ):
        loop_interfaces_input_output_var_pairs.append((input, output))

    # For each variable going through the loop interface in main, if it then
    # goes through the loop decision node, create an edge from the original
    # output var of the interface to where the decision variable goes.
    for input_var, output_var in loop_interfaces_input_output_var_pairs:
        output_succs = list(dynamics_grfn.successors(output_var))
        for output_var_succ in output_succs:
            if output_var_succ.func_type == LambdaType.DECISION:
                var_after_decision = [
                    v
                    for v in dynamics_grfn.successors(output_var_succ)
                    if v.identifier.var_name == output_var.identifier.var_name
                ][0]
                for new_output_var_succ in dynamics_grfn.successors(var_after_decision):
                    dynamics_grfn.add_edge(output_var, new_output_var_succ)
                remove_node_and_hyper_edges(dynamics_grfn, var_after_decision)

    output_decision_node = [
        node
        for node in loop_decisions
        if len(list(grfn.predecessors(node)))
        == ((len(list(grfn.successors(node))) * 2) + 1)
    ][0]
    for succ in dynamics_grfn.successors(loop_output_interface):
        for decision_pred in dynamics_grfn.predecessors(output_decision_node):
            if decision_pred.identifier.var_name == succ.identifier.var_name:
                for src, _ in list(dynamics_grfn.in_edges(decision_pred)):
                    # dynamics_grfn.remove_edge(src, decision_pred)
                    # dynamics_grfn.add_edge(src, succ)
                    # to_remove.add(decision_pred)
                    var_output_edge_matches = [
                        h
                        for h in dynamics_grfn.hyper_edges
                        if decision_pred in h.outputs
                    ]
                    if len(var_output_edge_matches) > 0:
                        var_output_edge = var_output_edge_matches[0]
                        var_output_idx = [
                            idx
                            for idx, v in enumerate(var_output_edge.outputs)
                            if decision_pred.uid == v.uid
                            if decision_pred.uid == v.uid
                        ][0]
                        var_output_edge.outputs[var_output_idx] = succ
                        dynamics_grfn.add_edge(src, succ)
                    remove_node_and_hyper_edges(dynamics_grfn, decision_pred)
                break

    to_remove.update(dynamics_grfn.successors(output_decision_node))

    # Now that we have created new edges ignoring the decision node, remove
    # the decision nodes
    for loop_decision in loop_decisions:
        remove_node_and_hyper_edges(dynamics_grfn, loop_decision)

    # For each subgraph within the loop, add an edge from the grfn root
    # subgraph to it, move nodes from loop to root subgraph, and track
    # these variables
    loop_nodes_to_preserve = set()
    for loop_succ in loop_successors:
        loop_succ.parent = dynamics_grfn.root_subgraph.uid
        dynamics_grfn_subgraphs_graph.add_edge(dynamics_grfn.root_subgraph, loop_succ)
        loop_succ_interface = get_input_interface_node(dynamics_grfn, loop_succ)
        loop_succ_interface_pred = set(dynamics_grfn.predecessors(loop_succ_interface))
        # Find potential paths to this loop successors interface
        paths_to_interface = all_simple_paths(
            dynamics_grfn, loop_interface, loop_succ_interface
        )
        interface_hyper_edge_inputs = list()
        # for each path found to this interface
        for path in paths_to_interface:
            # for each node on the path, if it is from the loop subgraph,
            # add it into the root subgraph
            for node in path:
                if node != loop_interface and node in loop.nodes:
                    dynamics_grfn.root_subgraph.nodes.append(node)
                    loop_nodes_to_preserve.add(node)
                    if (
                        node in loop_succ_interface_pred
                        and node not in interface_hyper_edge_inputs
                    ):
                        interface_hyper_edge_inputs.append(node)

        existing_hyper_edges = [
            h
            for h in dynamics_grfn.hyper_edges
            if isinstance(h.lambda_fn, LambdaNode)
            and h.lambda_fn.uid == loop_succ_interface.uid
        ]
        if len(existing_hyper_edges) > 0:
            dynamics_grfn.hyper_edges = [
                h for h in dynamics_grfn.hyper_edges if h != existing_hyper_edges[0]
            ]
            dynamics_grfn.hyper_edges.append(
                HyperEdge(
                    interface_hyper_edge_inputs,
                    loop_succ_interface,
                    existing_hyper_edges[0].outputs,
                )
            )

        # Preserve the output vars of the loop successors we are keeping
        loop_succ_output_interface = loop_succ.get_output_interface_node(
            dynamics_grfn.hyper_edges
        )
        for v in loop_succ_output_interface.outputs:
            dynamics_grfn.root_subgraph.nodes.append(v)
            loop_nodes_to_preserve.add(v)

        loop_nodes_to_preserve.add(loop_succ_interface)
        loop_nodes_to_preserve.add(loop_succ_output_interface)

    # Create an edge from the variable going through the loop interface in main
    # to wherever the output variable of the loop interface is going to.
    # Remove the output var node in the loop from the graph.
    for input_var, output_var in loop_interfaces_input_output_var_pairs:
        for output_var_succ in dynamics_grfn.successors(output_var):
            dynamics_grfn.add_edge(input_var, output_var_succ)
        for edge in dynamics_grfn.hyper_edges:
            for idx, input in enumerate(edge.inputs):
                if output_var == input:
                    edge.inputs[idx] = input_var
                    break

        remove_node_and_hyper_edges(dynamics_grfn, output_var)

    # Remove variables going out of the loop sugraph as the results in main
    loop_edges = [e for e in dynamics_grfn.hyper_edges if e.lambda_fn in loop.nodes]
    loop_output_interface_edge = loop.get_output_interface_node(loop_edges)
    for loop_output_var in loop_output_interface_edge.outputs:
        if loop_output_var not in loop_nodes_to_preserve:
            remove_node_and_hyper_edges(dynamics_grfn, loop_output_var)

    # Remove all loop nodes that we dont want to preserve from the grfn
    for node in loop.nodes:
        if node not in loop_nodes_to_preserve:
            remove_node_and_hyper_edges(dynamics_grfn, node)

    # Remove the model driver loop from the dynamics grfn
    dynamics_grfn_subgraphs_graph.remove_node(loop_copy)

    def remove_empty_path(node):
        if node in dynamics_grfn.nodes:
            node_succs = list(dynamics_grfn.successors(node))
            if len(node_succs) == 0:
                predecessors = dynamics_grfn.predecessors(node)
                remove_node_and_hyper_edges(dynamics_grfn, node)
                # TODO this works for now, but the node might not always
                # be in the root subgraph.
                # dynamics_grfn.root_subgraph.nodes.remove(node)
                for p in predecessors:
                    remove_empty_path(p)

    # Remove hanging variables (and there potential singular path) going into
    # the loop interface that are not used anymore. (This applies to variables
    # like a loop iterator "i" or variables only used in the condition.)
    for n in loop_interface_hyper_edge.inputs:
        if n not in loop_nodes_to_preserve:
            remove_empty_path(n)

    for l_node in [n for n in dynamics_grfn.nodes if isinstance(n, LambdaNode)]:
        # There is only one output with a literal node
        output_var = list(dynamics_grfn.successors(l_node))[0]
        if (
            # TODO maybe fix?
            l_node.func_type == LambdaType.LITERAL
            and len(list(dynamics_grfn.successors(output_var))) == 0
        ):
            to_remove.add(output_var)
            to_remove.add(l_node)

    for n in to_remove:
        remove_node_and_hyper_edges(dynamics_grfn, n)

    return dynamics_grfn


def extract_model_dynamics(grfn: GroundedFunctionNetwork):
    resulting_model_dynamics_grfns = []
    root_subgraph = grfn.root_subgraph
    root_successors = grfn.subgraphs.successors(root_subgraph)
    for succ in root_successors:
        if isinstance(succ, GrFNLoopSubgraph):
            extracted_dynamics = extract_dynamics_from_loop(grfn, succ)
            resulting_model_dynamics_grfns.append(extracted_dynamics)

    return resulting_model_dynamics_grfns
