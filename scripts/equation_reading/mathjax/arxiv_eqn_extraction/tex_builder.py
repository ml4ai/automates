# CREATING TEX FILES OF THE LATEX EQUATIONS 

import os, subprocess

# Template for the TeX files
def template(eqn, Preamble_DMO, Preamble_Macro):
    
    # writing tex document for respective eqn 
    temp1 = '\\documentclass{standalone}\n' \
               '\\usepackage{amsmath}\n' \
               '\\usepackage{amssymb}\n' 
    temp2 = '\\begin{document}\n' \
            f'$\\displaystyle {{{{ {eqn} }}}} $\n' \
            '\\end{document}'
    
    temp = temp1 + Preamble_DMO + Preamble_Macro + temp2
    return(temp)

# function to create tex documents for each eqn in the folder
def CreateTexDoc(eqn, keyword_dict, keyword_Macro_dict, tex_folder, TeX_name):
   
    # checking \DeclareMathOperator and Macros
    DeclareMathOperator_in_eqn = [kw for kw in keyword_dict.keys() if kw in eqn]
    Macros_in_eqn = [kw for kw in keyword_Macro_dict.keys() if kw in eqn]
    Preamble_DMO, Preamble_Macro = '', ''
    for d in DeclareMathOperator_in_eqn:
        Preamble_DMO += "{} \n".format(keyword_dict[d])
    for m in Macros_in_eqn:
        Preamble_Macro += "{} \n".format(keyword_Macro_dict[m])
            
    # creating tex file
    path_to_tex = os.path.join(tex_folder, "{}.tex".format(TeX_name))
    with open(path_to_tex, 'w') as f_input:
        f_input.write(template(eqn, Preamble_DMO, Preamble_Macro))
        f_input.close()

def main(latex_equations, tex_files):
    
    # loop through the folders
    for folder in os.listdir(latex_equations):     
        # creating tex folders for Large and Small equations
        tex_folder = os.path.join(tex_files, folder)
        TexFolder_Large_Eqn = os.path.join(tex_folder, "Large_eqns")
        TexFolder_Small_Eqn = os.path.join(tex_folder, "Small_eqns")
        for F in [tex_folder, TexFolder_Large_Eqn, TexFolder_Small_Eqn]:
            if not os.path.exists(F):   
                subprocess.call(['mkdir', F])
                    
        # reading eqns of paper from folder in latex_equations 
        path_to_folder = os.path.join(latex_equations, folder)
        LargeEqn_Path = os.path.join(path_to_folder, "Large_eqns")
        SmallEqn_Path = os.path.join(path_to_folder, "Small_eqns")
                                           
        # Dealing with "/DeclareMathOperator"
        DMO_file = os.path.join(path_to_folder, "DeclareMathOperator_paper.txt")
        with open(DMO_file, 'r') as file:
            DMO = file.readlines()
            file.close()
        
        # initializing /DeclareMathOperator dictionary
        keyword_dict={}
        for i in DMO:
            ibegin, iend = i.find('{'), i.find('}')
            keyword_dict[i[ibegin+1 : iend]] = i
        
        # Dealing with "Macros"
        Macro_file = os.path.join(path_to_folder, "Macros_paper.txt")
        with open(Macro_file, 'r') as file:
            Macro = file.readlines()
            file.close()
        
        # initializing /Macros dictionary
        keyword_Macro_dict={}
        for i in Macro:
            ibegin, iend = i.find('{'), i.find('}')
            keyword_Macro_dict[i[ibegin+1 : iend]] = i
        
        # Path to the folder containing Large and Small equations
        for Path in [LargeEqn_Path, SmallEqn_Path]:
            for File in os.listdir(Path):    
                main_file = os.path.join(Path, File)
                with open (main_file, 'r') as file:
                    eqn = file.readlines()
                    file.close()
                
                TeX_name = File.split(".")[0]
                # calling function to create tex doc for the particular folder --> giving all latex eqns, DMOs, Macros and tex_folder path as arguments
                if len(eqn)!=0:
                    if Path == LargeEqn_Path:
                        CreateTexDoc(eqn[0], keyword_dict, keyword_Macro_dict, TexFolder_Large_Eqn, TeX_name)
                    else:
                        CreateTexDoc(eqn[0], keyword_dict, keyword_Macro_dict, TexFolder_Small_Eqn, TeX_name) 

if __name__ == "__main__":
    
    for dir in ["1402", "1403", "1404", "1405"]:
        print(dir)
        # paths
        base_dir = f"/projects/temporary/automates/er/gaurav/{dir}_results"
        # Latex_equations directory
        latex_equations = os.path.join(base_dir, "latex_equations")
        # tex_files dumping directory
        tex_files = os.path.join(base_dir, "tex_files")
    
        main(latex_equations, tex_files)
