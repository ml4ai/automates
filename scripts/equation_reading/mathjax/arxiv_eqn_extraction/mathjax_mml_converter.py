# CONVERT LaTeX EQUATION TO MathML CODE USING MathJax

import requests
import subprocess, os
import json
import argparse

# Defining global dictionary and array to capture all the keywords not supported by MathJax and other erros respectively
keywords_log =[]
Errors = []

# Removing "\n", "\", and un-necessary qoutes 
def CleaningMML(res):
    # Removing "\ and /" at the begining and at the end
    res = res[res.find("<"):]
    res = res[::-1][res[::-1].find(">"):]
    res = res[::-1]
    # Removing "\\n"
    res = res.replace(">\\n", ">")
    return(res)
    
def Creating_Macro_DMO_dictionaries(folder):
    #print("in Creating_Macro_DMO_dictionaries")
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

def Creating_final_equations(ce, folder, keyword_Macro_dict, keyword_dict, Large_MML, Small_MML):
    #print("in Creating_final_equations")
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
            for tr in ["\\ensuremath", "\\xspace", "\\aligned", "\\endaligned", "\\span"]:
                string = string.replace(tr, "")
            
            # Correcting keywords written in an incorrect way
            for sub in string.split(" "):
                if "cong" in sub:
                    sub = sub.replace("\\cong", "{\\cong}")
                if "mathbb" in sub:
                    if sub[sub.find("\\mathbb")+7] != "{":
                        mathbb_parameter = sub[sub.find("\\newcommand")+12 : sub.find("}")].replace("\\", "")
                        sub = sub[:sub.find("\\mathbb")+7] + "{" + mathbb_parameter + "}" + sub[sub.find("\\mathbb")+7+len(mathbb_parameter):]
                if "mathbf" in sub:
                    if sub[sub.find("\\mathbf")+7] != "{":
                        mathbf_parameter = sub[sub.find("\\newcommand")+12 : sub.find("}")].replace("\\", "")
                        sub = sub[:sub.find("\\mathbf")+7] + "{" + mathbf_parameter + "}" + sub[sub.find("\\mathbf")+7+len(mathbf_parameter):]
                
                final_eqn += sub + " "     
            #print("final_eqn --> %s"%final_eqn)
            
            tempPath = "/projects/temporary/automates/er/gaurav/results_file/tempFile.txt"
            json.dump(final_eqn, open(tempPath, "w"))
            MML = Large_MML if EqnsType == "Large_eqns" else Small_MML
            main(folder, file_name, tempPath, MML)
        except:
            pass
    
def main(folder,file_name, tempPath, mml_path):
    #print("main")
    #print(eqn)
    
    # Define the webservice address
    webservice = "http://localhost:8081"
    # Load the LaTeX string data
    eqn = json.load(open(tempPath, "r"))
    #print(eqn)
    #print("++==++"*15)
    # Translate and save each LaTeX string using the NodeJS service for MathJax
    #mml_strs = list()
    
    res = requests.post(
        f"{webservice}/tex2mml",
        headers={"Content-type": "application/json"},
        json={"tex_src": json.dumps(eqn)},
         )
    #print(res.text)
    # Capturing the keywords not supported by MathJax
    if "FAILED" in res.content.decode("utf-8"):
        # Just to check errors
        TeXParseError = res.content.decode("utf-8").split("::")[1]
        # Logging incorrect/ unsupported keywords along with their equations
        if "Undefined control sequence" in TeXParseError:
            Unsupported_Keyword = TeXParseError.split("\\")[-1]
            if Unsupported_Keyword not in keywords_log:
                keywords_log.append(Unsupported_Keyword)
        # Logging errors other than unsupported keywords
        else:
            if TeXParseError not in Errors:
                Errors.append(TeXParseError)
                
    else:
        # Dump the MathML strings to JSON file
        MML = CleaningMML(res.text)
        json.dump(MML, open(os.path.join(mml_path, f"{file_name}.txt"), "w"))

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
        # Creating folder for Large and Small eqns
        Large_MML = os.path.join(mml_folder, "Large_MML")
        Small_MML = os.path.join(mml_folder, "Small_MML")
        for F in [mml_folder, Large_MML, Small_MML]:
            if not os.path.exists(F):
                subprocess.call(['mkdir', F])
        
        # Creating Macros dictionary
        keyword_Macro_dict, keyword_dict = Creating_Macro_DMO_dictionaries(folder)
        
        '''Appending all the eqns of the folder/paper to Latex_strs_json 
        along with their respective Macros and Declare Math Operator commands.'''
        # Creating array of final eqns
        Large_correct_eqns = os.path.join(folder_correct_latex_eqns, f"{folder}/Large_eqns")
        Small_correct_eqns = os.path.join(folder_correct_latex_eqns, f"{folder}/Small_eqns")
        for ce in [Large_correct_eqns, Small_correct_eqns]:
            Creating_final_equations(ce, folder, keyword_Macro_dict, keyword_dict, Large_MML, Small_MML)
            
          
    print(keywords_log)
    print(" ")
    print(" ====================== Errors ======================")
    print(" ")
    print(Errors)
    json.dump(keywords_log, open("/projects/temporary/automates/er/gaurav/results_file/MathJax_Logs/Keywords_logs.txt", "w"))  
    json.dump(Errors, open("/projects/temporary/automates/er/gaurav/results_file/MathJax_Logs/Errors_logs.txt", "w"))  

