# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 23:17:51 2020

@author: gaura

Latex eqns to mml converter using "Latex2mml" lib

NOTE: to get all the eqns not producing mml can be found in "errors" >> as output files named "Bad_eqns".
"""
import json
import latex2mathml.converter   

# function for creating MathML equation representation
def MathML(strEquation):
    latex_input = strEquation
    mathml_output = latex2mathml.converter.convert(latex_input)
    return mathml_output

# array containing all the scr-mml eqns 
src_mml_array = []

# array to store errors
error = []

# importing the src_latex file containing all the parsed and cleaned latex eqns
n_papers = 6
for n_paper in range(1, n_papers):
    
    # initializing the array -- for storing mml output of each paper latex eqns
    mml = []

    with open(r'C:\Users\gaura\OneDrive\Desktop\AutoMATES\REPO\results_file\paper{}\src_latex_paper{}.txt'.format(n_paper, n_paper), 'r') as file:
        CleanedEqns = file.readlines()
    
    for i, cleaned_eq in enumerate(CleanedEqns):
        try:
            mml_output = MathML(cleaned_eq)
            #print(mml_output)
            mml.append(mml_output)
            
            # appending the eqns in src_mml array
            temp_dict = {} 
            temp_dict['src'] = cleaned_eq
            temp_dict['mml'] = mml_output
            src_mml_array.append(temp_dict)
        
        except:
            error.append(["src_latex_paper {} -- eqn number {}".format(n_paper, i)])
            print('src_latex_paper {} -- eqn number {} has wrong latex format'.format(n_paper, i))
            #pass
        
    # dumping the output file --> mml_code_latex2mml as json file
    with open(r'C:\Users\gaura\OneDrive\Desktop\AutoMATES\REPO\results_file\paper{}\mml_code_latex2mml_paper{}.txt'.format(n_paper, n_paper), 'w') as file:
        json.dump(mml, file, indent = 4)

# dumping all src-mml pairs --> src_mml_array as json file
with open(r'C:\Users\gaura\OneDrive\Desktop\AutoMATES\REPO\results_file\src_mml_array.txt', 'w') as file:
    json.dump(src_mml_array, file, indent = 4)

# dumping all errors --> Bad eqns as json file
with open(r'C:\Users\gaura\OneDrive\Desktop\AutoMATES\REPO\results_file\Bad_eqns.txt', 'w') as file:
    json.dump(error, file, indent = 4)
