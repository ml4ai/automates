# CONVERT LaTeX EQUATION TO MathML CODE USING MathJax

import requests
import subprocess, os
import json
import argparse

# Defining global array to capture all the keywords not supported by MathJax
keywords_log = []

def main(eqn_file, mml_path):
    # Define the webservice address
    webservice = "http://localhost:8081"
    # Load the LaTeX string data
    latex_strs = json.load(open(eqn_file, "r"))
    
    # Translate and save each LaTeX string using the NodeJS service for MathJax
    mml_strs = list()
    for latex in latex_strs:
        res = requests.post(
            f"{webservice}/tex2mml",
            headers={"Content-type": "application/json"},
            json={"tex_src": json.dumps(latex)},
             )
        
        # Capturing the keywords not supported by MathJax
        if "FAILED" in res.content.decode("utf-8"):
            #print("=="*10)
            Unsupported_Keyword = res.content.decode("utf-8").split("::")[1].split("\\")[-1]
            keywords_log.append(Unsupported_Keyword)

        # Save the MML text response to our list
        mml_strs.append(res.text)

    # Dump the MathML strings to JSON
    json.dump(mml_strs, open(mml_path, "w"))

def Creating_Macro_DMO_dictionaries(folder):
    Macro_file = os.path.join(root, f"latex_equations/{folder}/Macros_paper.txt")
    with open(Macro_file, 'r') as file:
        Macro = file.readlines()
        file.close()
    keyword_Macro_dict={}
    for i in Macro:
        ibegin, iend = i.find('{'), i.find('}')
        keyword_Macro_dict[i[ibegin+1 : iend]] = i
    
    # Creating DMO dictionary
    DMO_file = os.path.join(root, f"latex_equations/{folder}/DeclareMathOperator_paper.txt")
    with open(DMO_file, 'r') as file:
        DMO = file.readlines()
        file.close()
    keyword_dict={}
    for i in DMO:
        ibegin, iend = i.find('{'), i.find('}')
        keyword_dict[i[ibegin+1 : iend]] = i
    
    return(keyword_Macro_dict, keyword_dict)

def Creating_final_equations(ce, folder, keyword_Macro_dict, keyword_dict, to_remove):
    Latex_strs_json = []       
    for index, eqn in enumerate(os.listdir(ce)):
        file_name = eqn.split(".")[0]
        EqnsType = "Large_eqns" if ce == Large_correct_eqns else "Small_eqns"
        file_path = os.path.join(root, f"latex_equations/{folder}/{EqnsType}/{file_name}.txt")
        final_eqn = ""
        try:
            text_eqn = open(file_path, "r").readlines()[0]
            Macros_in_eqn = [kw for kw in keyword_Macro_dict.keys() if kw in text_eqn]
            DMOs_in_eqn = [kw for kw in keyword_dict.keys() if kw in text_eqn]
                
            # Writing Macros, DMOs, and text_eqn as one string
            MiE, DiE = "", ""
            for macro in Macros_in_eqn:
                MiE = MiE + keyword_Macro_dict[macro] + " "
            for dmo in DMOs_in_eqn:
                DiE = DiE +  keyword_dict[dmo] + " "    
            string = MiE + DiE + text_eqn
            
            # Removing unsupported keywords 
            for tr in to_remove:
                string = string.replace(tr, "")
            
            # Correcting keywords written in an incorrect way
            for sub in string.split(" "):
                if "cong" in sub:
                    sub = sub.replace("\\cong", "{\\cong}")
                if "mathbb" in sub:
                    if sub[sub.find("\\mathbb")+7] != "{":
                        mathbb_parameter = sub[sub.find("\\newcommand")+12 : sub.find("}")].replace("\\", "")
                        sub = sub[:sub.find("\\mathbb")+7] + "{" + mathbb_parameter + "}" + sub[sub.find("\\mathbb")+7+len(mathbb_parameter):]
                
                final_eqn += sub + " "     
                                      
            Latex_strs_json.append(final_eqn)
        except:
            pass
    
    return(Latex_strs_json)

if __name__ == "__main__":
    # Paths
    root = "/projects/temporary/automates/er/gaurav/results_file"
    # Path to directory containing correct latex eqns
    folder_correct_latex_eqns = os.path.join(root, "latex_correct_equations")
    # Path to directory contain MathML eqns
    mml_dir = os.path.join(root, "Mathjax_mml")
    
    for folder in os.listdir(folder_correct_latex_eqns):
        # Creating folder for MathML codes for specific file
        mml_folder = os.path.join(mml_dir, folder)
        if not os.path.exists(mml_folder):
            subprocess.call(['mkdir', mml_folder])
        
        # Creating Macros dictionary
        keyword_Macro_dict, keyword_dict = Creating_Macro_DMO_dictionaries(folder)
        # Keywords to remove
        to_remove = ["\\ensuremath", "\\xspace", "\\aligned", "\\endaligned", "\\span"]
        
        '''Appending all the eqns of the folder/paper to Latex_strs_json 
        along with their respective Macros and Declare Math Operator commands.'''
        # Creating array of final eqns
        Large_correct_eqns = os.path.join(folder_correct_latex_eqns, f"{folder}/Large_eqns")
        Small_correct_eqns = os.path.join(folder_correct_latex_eqns, f"{folder}/Small_eqns")
        for ce in [Large_correct_eqns, Small_correct_eqns]:
            Latex_strs_json = Creating_final_equations(ce, folder, keyword_Macro_dict, keyword_dict, to_remove)
            
            # Making directories and dumping Latex_strs_json
            JSON_dir_folder = os.path.join(root, f"JSON_dir/{folder}")                           
            if not os.path.exists(JSON_dir_folder):
                subprocess.call(["mkdir", JSON_dir_folder])

            # calling main(arg1, arg2) --> arg1: path to json file containing latex eqns
            # args2: path to the json file to store converted mml eqns.      
            if ce == Large_correct_eqns:
                json.dump(Latex_strs_json, open(os.path.join(JSON_dir_folder, "LargeStrings.txt"),"w"))
                main(os.path.join(JSON_dir_folder, "LargeStrings.txt"), os.path.join(mml_folder, "LargeEqns_MML.txt"))
            else:
                json.dump(Latex_strs_json, open(os.path.join(JSON_dir_folder, "SmallStrings.txt"),"w"))
                main(os.path.join(JSON_dir_folder, "SmallStrings.txt"), os.path.join(mml_folder, "SmallEqns_MML.txt")) 
     
    pritn(keywords_log)
    json.dump(keywords_log, open("/projects/temporary/automates/er/gaurav/results_file/MathJax_logs.txt", "w"))  
