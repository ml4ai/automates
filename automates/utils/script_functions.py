import ast
import dill
import os.path
import json
# import astpp

from automates.gromet.fn import (
    GrometFNModuleCollection,
)

from automates.utils.fold import dictionary_to_gromet_json, del_nulls
from automates.program_analysis.PyAST2CAST import py_ast_to_cast
from automates.program_analysis.CAST2GrFN import cast 
from automates.program_analysis.CAST2GrFN.model.cast import SourceRef
from automates.program_analysis.CAST2GrFN.cast import CAST
from automates.program_analysis.CAST2GrFN.visitors.cast_to_agraph_visitor import CASTToAGraphVisitor
from automates.program_analysis.CAST2GrFN.ann_cast.cast_to_annotated_cast import CastToAnnotatedCastVisitor
from automates.program_analysis.CAST2GrFN.ann_cast.id_collapse_pass import IdCollapsePass
from automates.program_analysis.CAST2GrFN.ann_cast.container_scope_pass import ContainerScopePass
from automates.program_analysis.CAST2GrFN.ann_cast.variable_version_pass import VariableVersionPass
from automates.program_analysis.CAST2GrFN.ann_cast.grfn_var_creation_pass import GrfnVarCreationPass
from automates.program_analysis.CAST2GrFN.ann_cast.grfn_assignment_pass import GrfnAssignmentPass
from automates.program_analysis.CAST2GrFN.ann_cast.lambda_expression_pass import LambdaExpressionPass
from automates.program_analysis.CAST2GrFN.ann_cast.to_grfn_pass import ToGrfnPass
from automates.program_analysis.CAST2GrFN.ann_cast.to_gromet_pass import ToGrometPass


def process_file_system(system_name, path, files, write_to_file=False):
    root_dir = path.strip()
    file_list = open(files,"r").readlines()

    module_collection = GrometFNModuleCollection(schema_version="0.1.5", name=system_name, modules=[], module_index=[], executables=[])

    for f in file_list:
        full_file = os.path.join(os.path.normpath(root_dir), f.rstrip("\n"))
        
        # Open the file
        # TODO: Do we want to open the CAST or the Python source? 
        #  If we open the Python source then we need to generate its CAST and then generate its GroMEt after
        #  I'm thinking for now we open the CAST, and generate GroMEt
        #  As a next-step we can incorporate the Python -> CAST step
        print(full_file.rstrip())
        
        try:
            cast = python_to_cast(full_file, cast_obj=True)
            generated_gromet = ann_cast_pipeline(cast, gromet=True, to_file=False, from_obj=True)

            # Then, after we generate the GroMEt we store it in the 'modules' field 
            # and store its path in the 'module_index' field
            module_collection.modules.append(generated_gromet)
            
            # DONE: Change this so that it's the dotted path from the root
            # i.e. like model.view.sir" like it shows up in Python
            source_directory = os.path.basename(os.path.normpath(root_dir)) # We just need the last directory of the path, not the complete path 
            os_module_path = os.path.join(source_directory, f)
            python_module_path = os_module_path.replace("/", ".").replace(".py","")
            module_collection.module_index.append(python_module_path)

            # Done: Determine how we know a gromet goes in the 'executable' field
            # We do this by finding all user_defined top level functions in the Gromet
            # and check if the name 'main' is among them 
            function_networks = [fn.value for fn in generated_gromet.attributes if fn.type == "FN"]
            defined_functions = [fn.b[0].name for fn in function_networks if fn.b[0].function_type == "FUNCTION"]
            if "main" in defined_functions:
                module_collection.executables.append(python_module_path)

        except ImportError:
            print("FAILURE")
        
        
    # After we go through the whole system, we can then write out the module_collection
    if write_to_file:
        with open(f"{system_name}--Gromet-FN-auto.json","w") as f:
            gromet_collection_dict = module_collection.to_dict()
            f.write(dictionary_to_gromet_json(del_nulls(gromet_collection_dict)))

    return module_collection

def python_to_cast(pyfile_path, agraph=False, astprint=False, std_out=False, rawjson=False, legacy=False, cast_obj=False):
    # Open Python file as a giant string
    file_handle = open(pyfile_path)
    file_contents = file_handle.read()
    file_handle.close()
    file_name = pyfile_path.split("/")[-1]

    # Count the number of lines in the file
    file_handle = open(pyfile_path)
    file_list = file_handle.readlines()
    line_count = 0
    for l in file_list:
        line_count += 1
    file_handle.close()

    # Create a PyASTToCAST Object
    if legacy:
        convert = py_ast_to_cast.PyASTToCAST(file_name, legacy=True)
    else:
        convert = py_ast_to_cast.PyASTToCAST(file_name)

    # Additional option to allow us to view the PyAST 
    # using the astpp module 
    if astprint:
        # astpp.parseprint(file_contents)
        pass

    # 'Root' the current working directory so that it's where the 
    # Source file we're generating CAST for is (for Import statements)
    old_path = os.getcwd()
    idx = pyfile_path.rfind("/")

    if idx > -1:
        curr_path = pyfile_path[0:idx]
        os.chdir(curr_path)
    else:
        curr_path = "./"+pyfile_path

    #os.chdir(curr_path)

    # Parse the python program's AST and create the CAST
    contents = ast.parse(file_contents)
    C = convert.visit(contents, {}, {})
    C.source_refs = [SourceRef(file_name, None, None, 1, line_count)]

    os.chdir(old_path)
    out_cast = cast.CAST([C], "python")

    if agraph:
        V = CASTToAGraphVisitor(out_cast)
        last_slash_idx = file_name.rfind("/")
        file_ending_idx = file_name.rfind(".")
        pdf_file_name = f"{file_name[last_slash_idx + 1 : file_ending_idx]}.pdf"
        V.to_pdf(pdf_file_name)

    # Then, print CAST as JSON
    if cast_obj:
        return out_cast
    else:
        if rawjson:
            print(json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None))
        else:
            if std_out:
                print(out_cast.to_json_str())
            else:
                out_name = file_name.split(".")[0]
                print("Writing CAST to "+out_name+"--CAST.json")
                out_handle = open(out_name+"--CAST.json","w")
                out_handle.write(out_cast.to_json_str())



def ann_cast_pipeline(cast_instance, to_file=True, gromet=False, grfn_2_2=False, a_graph=False, from_obj=False):
    """cast_to_annotated.py

    This function reads a JSON file that contains the CAST representation
    of a program, and transforms it to annotated CAST. It then calls a
    series of passes that each augment the information in the annotatd CAST nodes
    in preparation for the GrFN generation.
   
    One command-line argument is expected, namely the name of the JSON file that
    contains the CAST data.
    TODO: Update this docstring as the program has been tweaked so that this is a function instead of
    the program
    """

    if from_obj:
        f_name = ""
        cast = cast_instance
    else:
        f_name = cast_instance
        f_name = f_name.split("/")[-1]
        f_name = f_name.replace("--CAST.json", "")
        file_contents = open(f_name, "r").read()

        cast_json = CAST([], "python")
        cast = cast_json.from_json_str(file_contents)

    visitor = CastToAnnotatedCastVisitor(cast)
    # The Annotated Cast is an attribute of the PipelineState object
    pipeline_state = visitor.generate_annotated_cast(grfn_2_2)

    # TODO: make filename creation more resilient

    print("Calling IdCollapsePass------------------------")
    IdCollapsePass(pipeline_state)

    print("\nCalling ContainerScopePass-------------------")
    ContainerScopePass(pipeline_state)

    print("\nCalling VariableVersionPass-------------------")
    VariableVersionPass(pipeline_state)

    # NOTE: CASTToAGraphVisitor uses misc.uuid, so placing it here means
    # that the generated GrFN uuids will not be consistent with GrFN uuids
    # created during test runtime. So, do not use these GrFN jsons as expected 
    # json for testing
    if a_graph:
        agraph = CASTToAGraphVisitor(pipeline_state)
        pdf_file_name = f"{f_name}-AnnCast.pdf"
        agraph.to_pdf(pdf_file_name)

    print("\nCalling GrfnVarCreationPass-------------------")
    GrfnVarCreationPass(pipeline_state)

    print("\nCalling GrfnAssignmentPass-------------------")
    GrfnAssignmentPass(pipeline_state)

    print("\nCalling LambdaExpressionPass-------------------")
    LambdaExpressionPass(pipeline_state)
    
    if gromet:
        print("\nCalling ToGrometPass-----------------------")
        ToGrometPass(pipeline_state)
        
        if to_file:
            with open(f"{f_name}--Gromet-FN-auto.json","w") as f:
                gromet_collection_dict = pipeline_state.gromet_collection.to_dict()
                f.write(dictionary_to_gromet_json(del_nulls(gromet_collection_dict)))
        else:
            return pipeline_state.gromet_collection
    else:
        print("\nCalling ToGrfnPass-------------------")
        ToGrfnPass(pipeline_state)
        grfn = pipeline_state.get_grfn()
        grfn.to_json_file(f"{f_name}--AC-GrFN.json")

        grfn_agraph = grfn.to_AGraph()
        grfn_agraph.draw(f"{f_name}--AC-GrFN.pdf", prog="dot")

        print("\nGenerating pickled AnnCast nodes-----------------")
        pickled_file_name = f"{f_name}--AnnCast.pickled"
        with open(pickled_file_name,"wb") as pkfile:
            dill.dump(pipeline_state, pkfile)

