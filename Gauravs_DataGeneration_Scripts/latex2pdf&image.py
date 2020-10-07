# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 11:34:47 2020

@author: gaura

latex src eqns to ".png" images

NOTE: Please change the paths as per your system
"""
import os, json
import subprocess
from shutil import copyfile
from pdf2image import convert_from_path


# creating a template for tex file
def template(eqn, DMOineqn, Macroineqn):
    # arranging \DeclareMathOpertaor
    
    DMOeqn= ''
    for d in DMOineqn:
        DMOeqn += "{} \n".format(d)
    
    Macroeqn= ''
    for m in Macroineqn:
        Macroeqn += "{} \n".format(m)
    
    '''
    temp ='\\documentclass{standalone}\n' \
               '\\usepackage{amsmath}\n' \
               '\\usepackage{amssymb}\n' \
               f'{k} \n' \
               '\\begin{document}\n' \
               f'$\\displaystyle {{{{ {eqn} }}}} $\n' \
               '\\end{document}'
    '''
    # writing tex document for respective eqn 
    temp1 = '\\documentclass{standalone}\n' \
               '\\usepackage{amsmath}\n' \
               '\\usepackage{amssymb}\n' 
    temp2 = '\\begin{document}\n' \
            f'$\\displaystyle {{{{ {eqn} }}}} $\n' \
            '\\end{document}'
    
    temp = temp1 + Macroeqn + DMOeqn + temp2
    return(temp)

# function to create tex documents for each eqn in the folder
def CreateTexDoc(eqns, keyword_dict, keyword_Macro_dict, tex_folder):
    # creating tex files of the eqns
    for index, eqn in enumerate(eqns):
        # checking \DeclareMathOperator and Macros
        DeclareMathOperator_in_eqn = [kw for kw in keyword_dict.keys() if kw in eqn]
        Macros_in_eqn = [kw for kw in keyword_Macro_dict.keys() if kw in eqn]
        # creating tex file
        path_to_tex = os.path.join(tex_folder, "eqn{}.tex".format(index))
        with open(path_to_tex, 'w') as f_input:
            tex_file = f_input.write(template(eqn, DeclareMathOperator_in_eqn, Macros_in_eqn))
            f_input.close()

# create pdf files for the tex documents of the folder
def CreatePdf(tex_folder, pdf_folder, correct_tex_folder):
    for index, tex in enumerate(os.listdir(tex_folder)):
        # grabbing tex document in tex folder
        path_to_tex = os.path.join(tex_folder, tex)
        # calling the tex documnets and running and storing pdf files generated via "pdflatex".
        os.chdir(pdf_folder)
        value = subprocess.Popen(['pdflatex',path_to_tex])
        value.communicate()
        retcode = value.returncode
        if not retcode == 0:
            os.unlink("{}.pdf".format(tex.split(".")[0]))

        # appending correct tex documents
        else:
            # copy correct tex documents form the tex_folder to correct_tex_folder
            src, dst = path_to_tex, os.path.join(correct_tex_folder,tex)
            copyfile(src, dst)

        # removing log and aux file
        os.unlink("{}.log".format(tex.split(".")[0]))
        subprocess.call(['rm','-rf', '{}.aux'.format(tex.split(".")[0])])
        subprocess.call(['rm','-rf', '{}.log'.format(tex.split(".")[0])])
    
# create images of the correct tex documents --> using pdf file 
def CreateImages(pdf_folder, image_folder):
    for index, pdf in enumerate(os.listdir(pdf_folder)):
        # extracting the image of the pdf
        path_to_pdf = os.path.join(pdf_folder, pdf) 
        output_file = '{}'.format(index)
        os.chdir(image_folder)
        img = convert_from_path(path_to_pdf, fmt = 'png', output_folder = image_folder, output_file=output_file)
    
# paths
base_dir = "/home/gauravs/Automates/results_file"
# Latex_equations directory
latex_equations = os.path.join(base_dir, "latex_equations")
# tex_files dumping directory
tex_files = os.path.join(base_dir, "tex_files")
# directory to dump pdf of the tex files
latex_pdf = os.path.join(base_dir, "latex_pdf")
# directory to dump images of the tex file equations
latex_images = os.path.join(base_dir, "latex_images")
# directory to dump correct latex equations
latex_correct_equations = os.path.join(base_dir, "latex_correct_equations")

# loop through the folders
for folder in os.listdir(latex_equations):
        
    # creating tex, pdf, image folders for each paper
    tex_folder = os.path.join(tex_files, folder)
    pdf_folder = os.path.join(latex_pdf, folder)
    image_folder = os.path.join(latex_images, folder)
    correct_tex_folder = os.path.join(latex_correct_equations, folder)
    for f in [tex_folder, pdf_folder, image_folder, correct_tex_folder]:
        if not os.path.exists(f):
            subprocess.call(['mkdir', f])
                
    # reading eqns of paper from folder in latex_equations 
    path_to_folder = os.path.join(latex_equations, folder)
    
    # Dealing with "/DeclareMathOperator"
    DMO_file = os.path.join(path_to_folder, "DeclareMathOperator_paper.txt")
    with open(DMO_file, 'r') as file:
        DMO = file.readline()
    
    # initializing /DeclareMathOperator dictionary
    keyword_dict={}
    for i in DMO:
        ibegin, iend = i.find('{'), i.find('}')
        keyword_dict[i[ibegin+1 : iend]] = i
    
    # Dealing with "Macros"
    Macro_file = os.path.join(path_to_folder, "Macros_paper.txt")
    with open(Macro_file, 'r') as file:
        Macro = file.readline()
    
    # initializing /DeclareMathOperator dictionary
    keyword_Macro_dict={}
    for i in Macro:
        ibegin, iend = i.find('{'), i.find('}')
        keyword_Macro_dict[i[ibegin+1 : iend]] = i
    
    
    # main_file = os.path.join(path_to_folder, "latex_equations.txt")
    for MF in os.listdir(path_to_folder):
        if MF != "DeclareMathOperator_paper.txt" or MF!= "Macros_paper.txt":
            main_file = os.path.join(path_to_folder, MF)
            with open (main_file, 'r') as file:
                eqns = file.readlines()
    '''
    # Dealing with "/DeclareMathOperator"
    DMO_file = os.path.join(path_to_folder, "DeclareMathOperator_paper.txt")
    with open(DMO_file, 'r') as file:
        DMO = file.readline()
    
    # initializing /DeclareMathOperator dictionary
    keyword_dict={}
    for i in DMO:
        ibegin, iend = i.find('{'), i.find('}')
        keyword_dict[i[ibegin+1 : iend]] = i
    '''
            # calling function to create tex doc for the particular folder --> giving all latex eqns, DMO, and tex_folder path as input
            CreateTexDoc(eqns, keyword_dict, keyword_Macro_dict, tex_folder)
    # create pdf of all the tex document we have just created using pdflatex
    CreatePdf(tex_folder, pdf_folder, correct_tex_folder)
    # create images of correct tex documents
    CreateImages(pdf_folder, image_folder)
   
