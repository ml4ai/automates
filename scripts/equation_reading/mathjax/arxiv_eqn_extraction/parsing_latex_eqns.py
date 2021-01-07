 # -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 23:02:49 2020
@author: gauravs
Latex eqns Parsing code
NOTE: Please change the paths as per your system before running the code.
"""

import pandas as pd
import json, os
from subprocess import call
import subprocess
import logging
import multiprocessing
import argparse
import chardet

from datetime import datetime
from multiprocessing import Pool, Lock, TimeoutError

# Printing starting time
start_time = datetime.now()
print('Starting at:  ', start_time)

# Defining global lock
lock = Lock()

# Argument Parser
parser = argparse.ArgumentParser(description='Parsing LaTeX equations from arxiv source codes')
parser.add_argument('-src', '--source', type=str, metavar='', required=True, help='Source path to arxiv folder')
parser.add_argument('-dst', '--destination', type=str, metavar='', required=True, help='Destination directory --> username directory')
parser.add_argument('-dir', '--directories', nargs='+', type=int, metavar='', required=True, help='List of directories to run')
parser.add_argument('-yr', '--year', type=str, metavar='', required=True, help='year of the directories')

group = parser.add_mutually_exclusive_group()
group.add_argument('-v', '--verbose', action='store_true', help='print verbose')
args = parser.parse_args()

# Setting up Logger - To get log files
Log_Format = '%(levelname)s:%(message)s'

logFile_dst = os.path.join(args.destination, str(args.year))

logging.basicConfig(filename = os.path.join(logFile_dst, 'unknown_Tex_Files.log'),  
                    level = logging.DEBUG, 
                    format = Log_Format, 
                    filemode = 'w')

logger = logging.getLogger()


def main():
    
    # possible matrix and equation keyword that can be used in LaTeX source codes
    matrix_cmds   = ['{matrix}', '{matrix*}', '{bmatrix}', '{bmatrix*}', '{Bmatrix}', '{Bmatrix*}', '{vmatrix}', '{vmatrix*}', '{Vmatrix}', '{Vmatrix*}']
    equation_cmds = ['{equation}', '{equation*}', '{align}', '{align*}', '{eqnarray}', '{eqnarray*}', '{displaymath}']
    
    # unknown encoding type
    unknown_iconv = ["unknown-8bit", "binary"]

    # get symbols, greek letter, and encoding list 
    excel_file = '/home/gauravs/Automates/automates_scripts/Latex_symbols.xlsx'
    df = pd.read_excel(excel_file, 'rel_optr')
    relational_operators = df.iloc[:, 0].values.tolist()
    df_greek = pd.read_excel(excel_file, 'greek')
    greek_letters = df_greek.iloc[:, 0].values.tolist()
    
    # looping through the latex paper directories
    src_path = args.source
    
    for DIR in args.directories:
        
        DIR = str(DIR)
        print(DIR)
        
        dir_path = os.path.join(src_path, DIR)
        
        destination = args.destination
        results_dir = os.path.join(destination, args.year)
        results_folder = os.path.join(results_dir, DIR)
        latex_equations = os.path.join(results_folder, 'latex_equations')
        
        if args.verbose:
            lock.acquire()
            print(' ===++=== '*15)
            print('Directory: ', DIR)
            print('Path to directoty: ', dir_path)
            print('Results folder: ', latex_equations)
            lock.release()
        
        for F in [results_dir, results_folder, latex_equations]:
            if not os.path.exists(F):
                subprocess.call(['mkdir', F])

        temp = []
        
        for tex_folder in os.listdir(dir_path):

            temp.append([latex_equations, matrix_cmds, equation_cmds, unknown_iconv, relational_operators, greek_letters, dir_path, tex_folder])
            
        with Pool(multiprocessing.cpu_count()) as pool:
            pool.map(Parse_equation, temp)   


def Parse_equation(args_list):
    
    global lock
    
    # Unpacking args_list
    (latex_equations, matrix_cmds, equation_cmds, unknown_iconv, relational_operators, greek_letters, dir_path, tex_folder) = args_list
    # Tex Folder path
    tex_folder_path = os.path.join(dir_path, tex_folder)
    
    if args.verbose:
        lock.acquire()
        print(' ')
        print('Running tex folder: ', tex_folder)
        lock.release()
        
    tex_file = [file for file in os.listdir(tex_folder_path) if ".tex" in file]
    
    # considering folders/papers with inly single tex file
    if len(tex_file) == 1:
        
        Tex_doc = os.path.join(tex_folder_path, tex_file[0])
        file = open(Tex_doc, 'rb')
        lines = file.readlines()
        encoding = chardet.detect(lines[0])['encoding']
        
        if args.verbose:
            lock.acquire()
            print('Encoding of the file:  ',encoding)
            lock.release()
            
        # Finding the type of encoding i.e. utf-8, ISO8859-1, ASCII, etc.   
        if encoding is not None:
            if encoding not in unknown_iconv:
            
                # initializing the arrays and variables
                total_macros = []
                declare_math_operator = []
                Line_largeEqn_dict = {}      # For large equations
                Line_inlineEqn_dict = {}     # For small inline equations
                Final_EqnNum_LineNum_dict = {}
                total_equations = []
                alpha = 0
                matrix = 0
                dollar = 1
                brac = 1

                # creating the paper folder
                root = latex_equations
                paper_dir = os.path.join(root,'{}'.format(tex_folder))
                if not os.path.exists(paper_dir):
                    call(['mkdir', paper_dir])

                # Making direstories for large and small eqns
                if not os.path.exists(os.path.join(paper_dir, "Large_eqns")):
                    call(['mkdir', os.path.join(paper_dir, "Large_eqns")]) 
                if not os.path.exists(os.path.join(paper_dir, "Small_eqns")):
                    call(['mkdir', os.path.join(paper_dir, "Small_eqns")]) 

                # opening files to write Macros and declare math operator
                MacroFile = open(os.path.join(root, '{}/Macros_paper.txt'.format(tex_folder)), 'w') 
                DMOFile = open(os.path.join(root, '{}/DeclareMathOperator_paper.txt'.format(tex_folder)), 'w')

                # since lines are in bytes, we need to convert them into str    
                for index, l in enumerate(lines):
                    line = l.decode(encoding, errors = 'ignore')

                    # extracting MACROS
                    if "\\newcommand" in line or "\\renewcommand" in line:
                        L = Macro(line)
                        if L is not None:
                            MacroFile.write(L)             

                    # extract declare math op:erator
                    if "\\DeclareMathOperator" in line:
                        DMOFile.write(line)

                    # condition 1.a: if $(....)$ is present
                    # condition 1.b: if $$(....)$$ is present --> replace it with $(---)$
                    if "$" in line or "$$" in line and alpha == 0:
                        # if line has any eqn
                        EqnFlag = True

                        if "$$" in line:
                            line = line.replace("$$", "$")

                        #array of the positions of the "$"
                        length = len([c for c in line if c=="$"])   

                        #length of the above array -- no. of the "$",  if even -- entire equation is in one line. If odd -- equation is going to next line
                        #if instead of $....$, $.... is present, and upto next 5 lines, no closing "$" can be found, then that condition will be rejected.
                        if length % 2 == 0:                          
                            inline_equation = inline(length, line)

                        else:
                            # combine the lines
                            try:
                                dol = 1
                                dol_indicator = False
                                while dol<6: #dollar != 0:
                                    line = line + lines[index + dol].decode(encoding, errors = "ignore") 
                                    if "$$" in line:
                                        line = line.replace("$$", "$") 

                                    length = len([c for c in line if c=="$"])
                                    if length%2 != 0:
                                        dol+=1
                                    else: 
                                        dol = 6
                                        dol_indicator = True

                                if dol_indicator:
                                    inline_equation = inline(length, line)
                                    
                                else:
                                    inline_equation = None
                            except:
                                 inline_equation = None

                        #check before appending if it is a valid equation
                        if inline_equation is not None:
                            r=[sym for sym in relational_operators if (sym in inline_equation)]
                            if bool(r):# == True:
                                total_equations.append(inline_equation)
                                Line_inlineEqn_dict[inline_equation] = index


                    # condition 2: if \[....\] is present
                    if "\\[" in line and alpha == 0:
                        EqnFlag = True
                        length_begin = len([c for c in line if c=="\\["])
                        length_end = len([c for c in line if c=="\\]"])

                        if length_begin == length_end:
                                Bequations = bracket_equation(line)
                        elif length_begin > length_end:
                            # combine the lines 
                            br = 1
                            while brac != 0:
                                line = line + lines[index + br].decode(encoding, errors = "ignore")
                                length_begin = len([c for c in line if c=="\\["])
                                length_end = len([c for c in line if c=="\\]"])
                                if length_begin == length_end:
                                    Bequations = bracket_equation(line)

                                else:
                                    br+=1
                        #check before appending if it is a valid equation
                        if Bequations is not None:
                            r=[sym for sym in relational_operators if (sym in Bequations)]
                            if bool(r):
                                total_equations.append(Bequations)
                                Line_inlineEqn_dict[Bequations] = index


                    # condition 3: if \(....\) is present
                    if "\\(" in line and alpha == 0:
                        length_begin = len([c for c in line if c=="\\("])
                        length_end = len([c for c in line if c=="\\)"])
                        if length_begin == length_end:
                                Pequations = parenthesis_equation(line)
                        elif length_begin > length_end:
                            # combine the lines 
                            br = 1
                            while brac != 0:
                                line = line + lines[index + br].decode(encoding, errors = "ignore")
                                length_begin = len([c for c in line if c=="\\("])
                                length_end = len([c for c in line if c=="\\)"])
                                if length_begin == length_end:
                                    Pequations = parenthesis_equation(line)
                                    
                                else:
                                    br+=1
                        #check before appending if it is a valid equation
                        if Pequations is not None:
                            r=[sym for sym in relational_operators if (sym in Pequations)]
                            if bool(r):# == True:
                                total_equations.append(Pequations)
                                Line_inlineEqn_dict[Pequations] = index

                    # condition 4: if \begin{equation(*)} \begin{case or split} --- \end{equation(*)} \begin{case or split}
                    # comdition 5: if \begin{equation(*)} --- \end{equation(*)}
                    for ec in equation_cmds:
                        if "\\begin{}".format(ec) in line:
                            begin_index_alpha = index+1
                            alpha = 1 

                    for ec in equation_cmds:
                        if "\\end{}".format(ec) in line and alpha == 1 : 
                            end_index_alpha = index
                            alpha =0

                            equation = lines[begin_index_alpha : end_index_alpha]
                            eqn = ''
                            for i in range(len(equation)):
                                eqn = eqn + equation[i].decode(encoding, errors = "ignore")
                            total_equations.append(eqn)
                            Line_largeEqn_dict[eqn] = index

                    # condition 6: if '\\begin{..matrix(*)}' but independent under condition 4
                    for mc in matrix_cmds:
                        if "\\begin{}".format(mc) in line and alpha == 0:
                            matrix = 1
                            begin_matrix_index = index

                        if "\\end{}".format(mc) in line and matrix == 1:
                            end_matrix_index = index
                            matrix =0

                            # append the array with the recet equation along with the \\begin{} and \\end{} statements
                            equation = lines[begin_matrix_index : end_matrix_index+1]
                            total_equations.append(equation)
                            Line_largeEqn_dict[List_to_Str(equation, encoding)] = index

                MacroFile.close()
                DMOFile.close()

                # Cleaning and Writing large and small eqns
                Final_EqnNum_LineNum_dict_large = Cleaning_writing_eqn(root, Line_largeEqn_dict, Final_EqnNum_LineNum_dict, encoding, tex_folder, matrix_cmds, LargeFlag=True)
                Final_EqnNum_LineNum_dict_small = Cleaning_writing_eqn(root, Line_inlineEqn_dict, Final_EqnNum_LineNum_dict, encoding, tex_folder, matrix_cmds, LargeFlag=False)

                # Dumping Final_EqnNum_LineNum_dict
                json.dump(Final_EqnNum_LineNum_dict_large, open(os.path.join(root, f"{tex_folder}/Eqn_LineNum_dict_large.txt"), "w"))
                json.dump(Final_EqnNum_LineNum_dict_small, open(os.path.join(root, f"{tex_folder}/Eqn_LineNum_dict_small.txt"), "w"))

            # if tex has unknown encoding or which can not be converted to some known encoding
            else:
                # Log the tex_folder that has unknown encoding
                lock.acquire()
                logger.debug(tex_folder)
                lock.release()
        else:
            lock.acquire()
            logger.debug(tex_folder)
            lock.release()


# to find inline equations i.e. $(...)$
def inline(length, line):
    pos = [pos for pos, char in enumerate(line) if char == "$"]
    #print(pos, length)
    if length%2 == 0:
        i = 0
        if length > 2:
            while i < length:
                inline_equation = line[pos[i]+1 : pos[i+1]]
                i = i+2
                return(inline_equation)

        else:
            inline_equation = line[pos[i]+1 : pos[i+1]]
            return(inline_equation)

# to find \[---\] equations
def bracket_equation(line):
    pos_begin = [pos for pos, char in enumerate(line) if char == "\\["]
    pos_end = [pos for pos, char in enumerate(line) if char == "\\]"]

    for i, j in zip(pos_begin, pos_end):
        equation = line[i+1 : j]

        return(equation)

# to find \(---\) equations
def parenthesis_equation(line):
    pos_begin = [pos for pos, char in enumerate(line) if char == "\\("]
    pos_end = [pos for pos, char in enumerate(line) if char == "\\)"]

    for i, j in zip(pos_begin, pos_end):
        parenthesis= line[i+1 : j]

        return(parenthesis)

# dealing with Macros
def Macro(line):    
    # checking the brackets
    open_curly_brac = [char for char in line if char == "{"]
    close_curly_brac = [char for char in line if char == "}"]
    if len(open_curly_brac)!= len(close_curly_brac):
        delta = len(open_curly_brac) - len(close_curly_brac)
        
        # if delta is positive --> need to close the brac
        if delta>0:
            for i in range(delta):
                line +="}"
        if delta < 0:
            for i in range(abs(delta)):
                line=line[:line.find(max(close_curly_brac))]

    try:
        # dealing with parameters assiging problem
        hash_flag = False
        line=line.replace(" ", "")
        var = [int(line[p+1]) for p, c in enumerate(line) if c == "#"]
        if len(var) !=0:
            if line[line.find("}")+1] != "[" and line[line.find("}")+3] != "]":     
                hash_flag = True
                max_var = max(var)
                temp = ""
                temp += line[:line.find("}")+1] + "[" + max_var + "]"+ line[line.find("}")+1:]
        
        if hash_flag:
            return temp
        else:
            return line
    except:
        pass

# creating a table having the mathml_output, latex code
latexCode_arr = []
mathml_output_arr = []
def DataSet(mathml_output, latex_code):
    mathml_output_arr.append(mathml_output)
    latexCode_arr.append(latex_code)

def List_to_Str(eqn, encoding):
    if type(eqn) is not list:
        return list
    else:
        # initialize an empty string
        s = ""
        for ele in eqn:
            ele = ele.decode(encoding, errors = "ignore")#("utf-8")
            s += ele
        return s


def Cleaning_writing_eqn(root, dictionary, Final_EqnNum_LineNum_dict, encoding, tex_folder, matrix_cmds, LargeFlag):
    
    global lock 
    
    src_latex, eq_dict= [], {}
    for e,line_num in dictionary.items():
        if type(e) is list:
            eq_dict[List_to_Str(e, encoding)] = line_num
        else:
            eq_dict[e] = line_num
    
    for i, eq in enumerate(eq_dict):
        if len(eq)!=0:
            # removing unnecc stuff - label, text, intertext
            par_clean_eq = Clean_eqn_1(eq)
            cleaned_eq = Clean_eqn_2(par_clean_eq, matrix_cmds)

            # sending the output to the dictionaries
            if cleaned_eq not in src_latex:
                src_latex.append(cleaned_eq)
                Final_EqnNum_LineNum_dict[f"eqn{i}"] = eq_dict[eq]
                
                if LargeFlag:
                    with open(os.path.join(root,f'{tex_folder}/Large_eqns/eqn{i}.txt'), 'w') as file:
                        lock.acquire()
                        print('+++===+++ '*10)
                        print(cleaned_eq)
                        lock.release()
                        
                        file.write(cleaned_eq)
                        file.close()
                else:
                    with open(os.path.join(root, f'{tex_folder}/Small_eqns/eqn{i}.txt'), 'w') as file:
                        lock.acquire()
                        print('+++===+++ '*10)
                        print(cleaned_eq)
                        lock.release()
                         
                        file.write(cleaned_eq)
                        file.close()
                        
    return(Final_EqnNum_LineNum_dict)

# cleaning eqn - part 1 --> removing label, text, intertext
def Clean_eqn_1(eqn_1):

    keywords_tobeCleaned = ["\\label", "\\text", "\\intertext"]
    for KC in keywords_tobeCleaned:
        try:
            if KC in eqn_1:
                p = 0
                while p == 0:
                    b = eqn_1.find(KC)
                    count = 1
                    k = 5
                    while count != 0:
                        if eqn_1[b+k] == "}":
                            count = 0 
                        else: 
                            k+=1
                    eqn_1 = eqn_1.replace(eqn_1[b:b+k+1], '')
                    if KC not in eqn_1:
                        p = 1
        except:
            pass
        
    return eqn_1 

#removing non-essential commands
def Clean_eqn_2(eqn_2, matrix_cmds):
    try:
        # removing "commas", "fullstop" and extra space at the end of the eqn
        eqn_2 = eqn_2.strip()
        if eqn_2[-1] == "," or eqn_2[-1] == ".":
            eqn_2 = eqn_2[:-1]
    except:
        pass

    # we don't want "&" in the equation as such untill unless it is a matrix
    if "&" in eqn_2:
        indicator_bmc = False
        for mc in matrix_cmds:
            bmc = "\\begin{}".format(mc)
            emc = "\\end{}".format(mc) 
            
            if bmc in eqn_2:
                indicator_bmc = True
                bmc_index = eqn_2.find(bmc)
                emc_index = eqn_2.find(emc)
                len_mc = len(mc)

            # position of "&" in equation
                list_of_and_symbol = [index_ for index_ ,char in enumerate(eqn_2) if char == "&"]     
                
            # index of the code in between bmc_index to emc_index 
            # don't need to remove "&" from this part eqn
                index_nochange = list(range(bmc_index+ 6+ len_mc+ 1, emc_index))
                
            # anywhere except index_nochange --> replace the "&" with ''   
                eqn_2_array = eqn_2.split("&")
                temp = ""
                for l in range(len(list_of_and_symbol)):
                    if list_of_and_symbol[l] in index_nochange:
                        temp += eqn_2_array[l] +  eqn_2_array[l+1]
                    else:
                        temp += eqn_2_array[l] + "&"+ eqn_2_array[l+1]
                eqn_2 = temp

        if not indicator_bmc:
            eqn_2=eqn_2.replace('&', '')

    return eqn_2


if __name__ == "__main__":
    main()
    
    # Printing stoping time
    stop_time = datetime.now()
    print('Stoping at:  ', stop_time)
    print(' ')
    print('parsing latex equations completed.')
