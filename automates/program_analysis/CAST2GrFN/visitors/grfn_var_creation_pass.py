import typing
from functools import singledispatchmethod

from automates.program_analysis.CAST2GrFN.visitors.annotated_cast import *

from automates.model_assembly.structures import (
    # GenericContainer,
    # LoopContainer,
    # GenericStmt,
    # CallStmt,
    # OperatorStmt,
    # LambdaStmt,
    GenericIdentifier,
    # ContainerIdentifier,
    VariableIdentifier,
    # TypeIdentifier,
    # ObjectDefinition,
    # VariableDefinition,
    # TypeDefinition,
    # GrFNExecutionException,
)

from automates.model_assembly.networks import (
    GenericNode,
    VariableNode
)

def create_grfn_var_from_name_node(node: AnnCastName):
    """
    Creates a `VariableNode` for this `AnnCastName` node.
    """
    con_scopestr = con_scope_to_str(node.con_scope)
    return create_grfn_var(node.name, node.id, node.version, con_scopestr)

def create_grfn_var(var_name:str, id: int, version: int, con_scopestr: str):
    """
    Creates a GrFN `VariableNode` using the parameters
    """
    # TODO: For now, we are passing in an empty Metadata
    # list.  We should update this to include the necessary
    # metadata
    # We may also need to update the namespace and scope 
    # we provide
    identifier = VariableIdentifier("default_ns", con_scopestr, var_name, version)

    # TODO: change to using UUIDs?
    # uid = GenericNode.create_node_id()
    uid = build_fullid(var_name, id, version, con_scopestr)
    # TODO: fill in metadata
    metadata = []
    return VariableNode(uid, identifier, metadata)

class GrfnVarCreationPass:
    def __init__(self, ann_cast: AnnCast):
        self.ann_cast = ann_cast
        self.nodes = self.ann_cast.nodes
        self.grfn_id_to_grfn_var = {}
        # the fullid of a AnnCastName node is a string which includes its variable name, numerical id,  version, and scope
        self.fullid_to_grfn_id = {}
        for node in self.ann_cast.nodes:
            self.visit(node)

        self.print_created_grfn_vars()
        self.store_grfn_state_in_ann_cast()

    def visit(self, node: AnnCastNode):
        """
        External visit that callsthe internal visit
        Useful for debugging/development.  For example,
        printing the nodes that are visited
        """
        # debug printing
        class_name = node.__class__.__name__
        print(f"\nProcessing node type {class_name}")

        # call internal visit
        return self._visit(node)

    def visit_node_list(self, node_list: typing.List[AnnCastNode]):
        return [self.visit(node) for node in node_list]

    def get_grfn_var_for_name_node(self, node: AnnCastName):
        """
        Obtains the GrFN variable node for the fullid of
        this AnnCastName node
        """
        fullid = ann_cast_name_to_fullid(node)
        return self.grfn_id_to_grfn_var[self.fullid_to_grfn_id[fullid]]

    def store_grfn_state_in_ann_cast(self):
        """
        Update annotated CAST to retain the GrFN variable data
        """
        self.ann_cast.fullid_to_grfn_id = self.fullid_to_grfn_id
        self.ann_cast.grfn_id_to_grfn_var = self.grfn_id_to_grfn_var

    def create_grfn_vars_helper(self, var_name: str, id: int, version: int, con_scopestr: str, endings: typing.List):
        """
        Create GrFN variables and cache them in GrFN state dicts.
        Uses the list of `endings` to generate additional variables for the branches of
        a ModelIf and Loop nodes
        """
        grfn_var = create_grfn_var(var_name, id, version, con_scopestr)
        fullid = build_fullid(var_name, id, version, con_scopestr)
        self.fullid_to_grfn_id[fullid] = grfn_var.uid
        self.grfn_id_to_grfn_var[grfn_var.uid] = grfn_var
        # link up the variables along each branch of endings to use the same GrFN variable
        for ending in endings:
            scopestr = con_scopestr + CON_STR_SEP + ending
            fullid = build_fullid(var_name, id, version, scopestr)
            self.fullid_to_grfn_id[fullid] = grfn_var.uid
        
    def create_grfn_vars_function_def(self, node: AnnCastFunctionDef):
        """
        Create GrFN `VariableNode`s for variables which are accessed
        or modified by this FunctionDef container
        This creates a version zero of all of these variables that will
        be used on the top interface
        """
        # union modified and accessed vars
        used_vars = {**node.modified_vars, **node.accessed_vars}
        con_scopestr = con_scope_to_str(node.con_scope)

        for id, var_name in used_vars.items():
            # we introduce version 0 at the top of the container
            version = 0
            endings = []
            self.create_grfn_vars_helper(var_name, id, version, con_scopestr, endings)

    def create_grfn_vars_model_if(self, node: AnnCastModelIf):
        """
        Create GrFN `VariableNode`s for variables which are accessed
        or modified by this ModelIf container
        This creates a version zero of all of these variables that will
        be used on the top interface
        """
        # union modified and accessed vars
        used_vars = {**node.modified_vars, **node.accessed_vars}
        con_scopestr = con_scope_to_str(node.con_scope)

        for id, var_name in used_vars.items():
            # we introduce version 0 at the top of the container
            version = 0
            endings = [IFEXPR, IFBODY, ELSEBODY]
            self.create_grfn_vars_helper(var_name, id, version, con_scopestr, endings)

        for id, var_name in node.modified_vars.items():
            # and we introduct version 1 to be used as the output of the Decision node
            # for modified variables
            version = 1
            endings = []
            self.create_grfn_vars_helper(var_name, id, version, con_scopestr, endings)

    def create_grfn_vars_loop(self, node: AnnCastLoop):
        """
        Create GrFN `VariableNode`s for variables which are accessed
        or modified by this Loop container
        This creates a version zero of all of these variables that will
        be used on the top interface
        """
        # union modified and accessed vars
        used_vars = {**node.modified_vars, **node.accessed_vars}
        con_scopestr = con_scope_to_str(node.con_scope)

        for id, var_name in used_vars.items():
            # we introduce version 0 at the top of a container
            version = 0
            endings = [LOOPEXPR, LOOPBODY]
            self.create_grfn_vars_helper(var_name, id, version, con_scopestr, endings)

    def print_created_grfn_vars(self):
        print("Created the follwing GrFN variables")
        print("-"*50)
        print(f"{'fullid':<50}{'grfn_id':<50}{'index':<10}")
        print(f"{'------':<50}{'-------':<50}{'-----':<10}")
        for fullid, grfn_id in self.fullid_to_grfn_id.items():
            grfn_var = self.grfn_id_to_grfn_var[grfn_id]
            print(f"{fullid:<50}{grfn_id:<50}{grfn_var.identifier.index:<10}")


    @singledispatchmethod
    def _visit(self, node: AnnCastNode):
        """
        Internal visit
        """
        raise NameError(f"Unrecognized node type: {type(node)}")

    @_visit.register
    def visit_assignment(self, node: AnnCastAssignment):
        # TODO: what if the rhs has side-effects
        self.visit(node.right)
        assert isinstance(node.left, AnnCastVar)
        self.visit(node.left)

    @_visit.register
    def visit_attribute(self, node: AnnCastAttribute):
        pass

    @_visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp):
        # visit LHS first
        self.visit(node.left)

        # visit RHS second
        self.visit(node.right)

    @_visit.register
    def visit_boolean(self, node: AnnCastBoolean):
        pass

    @_visit.register
    def visit_call(self, node: AnnCastCall):
        assert isinstance(node.func, AnnCastName)
        self.visit_node_list(node.arguments)

    @_visit.register
    def visit_class_def(self, node: AnnCastClassDef):
        pass

    @_visit.register
    def visit_dict(self, node: AnnCastDict):
        pass

    @_visit.register
    def visit_expr(self, node: AnnCastExpr):
        self.visit(node.expr)

    @_visit.register
    def visit_function_def(self, node: AnnCastFunctionDef):
        self.create_grfn_vars_function_def(node)
        self.visit_node_list(node.func_args)
        self.visit_node_list(node.body)

    @_visit.register
    def visit_list(self, node: AnnCastList):
        self.visit_node_list(node.values)

    @_visit.register
    def visit_loop(self, node: AnnCastLoop):
        self.create_grfn_vars_loop(node)
        # visit children
        self.visit(node.expr)
        self.visit_node_list(node.body)

    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak):
        pass

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue):
        pass

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf):
        self.create_grfn_vars_model_if(node)
        # visit children
        self.visit(node.expr)
        self.visit_node_list(node.body)
        self.visit_node_list(node.orelse)

    @_visit.register
    def visit_model_return(self, node: AnnCastModelReturn):
        self.visit(node.value)

    @_visit.register
    def visit_module(self, node: AnnCastModule):
        self.visit_node_list(node.body)

    @_visit.register
    def visit_name(self, node: AnnCastName):
        fullid = ann_cast_name_to_fullid(node)
        # if we haven't already created the GrFN `VariableNode`, create it
        if fullid not in self.fullid_to_grfn_id:
            grfn_var = create_grfn_var_from_name_node(node)
            self.fullid_to_grfn_id[fullid] = grfn_var.uid
            self.grfn_id_to_grfn_var[grfn_var.uid] = grfn_var

        # now, store the grfn_id in the nane node
        node.grfn_id = self.fullid_to_grfn_id[fullid]

    @_visit.register
    def visit_number(self, node: AnnCastNumber):
        pass

    @_visit.register
    def visit_set(self, node: AnnCastSet):
        pass

    @_visit.register
    def visit_string(self, node: AnnCastString):
        pass

    @_visit.register
    def visit_subscript(self, node: AnnCastSubscript):
        pass

    @_visit.register
    def visit_tuple(self, node: AnnCastTuple):
        pass

    @_visit.register
    def visit_unary_op(self, node: AnnCastUnaryOp):
        self.visit(node.value)

    @_visit.register
    def visit_var(self, node: AnnCastVar):
        self.visit(node.val)
