import argparse
import glob

import os.path

from automates.gromet.fn import (
    GrometFNModuleCollection,
)

from run_ann_cast_pipeline import ann_cast_pipeline
from python2cast import python_to_cast
from automates.utils.fold import dictionary_to_gromet_json, del_nulls
 
# python ../multi_file_ingester.py --sysname "chime_penn" --path "/Users/ferra/Desktop/Work_Repos/automates/scripts/program_analysis/CHIME_penn_full_model/penn_chime/" --files "system_filepaths.txt"
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sysname", type=str, help="The name of the system we're ingesting")
    parser.add_argument('--path', type=str, help='The path of source directory')
    parser.add_argument("--files", type=str, help='The path to a file containing a list of files to ingest')

    options = parser.parse_args()
    return options

def process_file_system(system_name, path, files):
    root_dir = path.strip()
    file_list = open(files,"r").readlines()

    module_collection = GrometFNModuleCollection(schema_version="0.1.5", name=system_name, modules=[], module_index=[], executables=[])

    for f in file_list:
        full_file = os.path.join(os.path.normpath(root_dir), f.strip("\n"))
        
        # Open the file
        # TODO: Do we want to open the CAST or the Python source? 
        #  If we open the Python source then we need to generate its CAST and then generate its GroMEt after
        #  I'm thinking for now we open the CAST, and generate GroMEt
        #  As a next-step we can incorporate the Python -> CAST step
        print(full_file)
        
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
    with open(f"{system_name}--Gromet-FN-auto.json","w") as f:
        gromet_collection_dict = module_collection.to_dict()
        f.write(dictionary_to_gromet_json(del_nulls(gromet_collection_dict)))




def main():
    args = get_args()

    system_name = args.sysname
    path = args.path
    files = args.files

    print(f"Ingesting system: {system_name}")
    print(f"With root directory as specified in: {path}")
    print(f"Ingesting the files as specified in: {files}")

    process_file_system(system_name, path, files)

    # TODO have path specified in command line
    # DONE correct end / in path file

main()

# files = glob.glob(path + '/**/*.py', recursive=True)
# print(files)
#for subdir, dirs, files in os.walk(path):
#    for dir in dirs:
#        pass # Recurse into dir
#    for file in files:
#        pass # Check if source code file
