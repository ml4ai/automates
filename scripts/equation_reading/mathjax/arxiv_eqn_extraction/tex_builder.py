# CREATING TEX FILES OF THE LATEX EQUATIONS 

import os, subprocess
import multiprocessing
import argparse

from datetime import datetime
from multiprocessing import Pool, Lock, TimeoutError

# Argument Parser
parser = argparse.ArgumentParser(description='Parsing LaTeX equations from arxiv source codes')
parser.add_argument('-src', '--source', type=str, metavar='', required=True, help='source directories')
parser.add_argument('-dir', '--directories', nargs="+", type=int, metavar='', required=True, help='directories to run')
parser.add_argument('-yr', '--year', type=int, metavar='', required=True, help='year')
args = parser.parse_args()

# Printing starting time
print(' ')
start_time = datetime.now()
print('Starting at:  ', start_time)


# Defining global lock
lock = Lock()


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

        #lock.acquire()
        f_input.write(template(eqn, Preamble_DMO, Preamble_Macro))
        f_input.close()
        #lock.release()

def main(args_list):

    #global lock 

    # Unpacking argments list
    (folder, tex_files) = args_list
    
    #lock.acquire()
    #print('current folder: ', folder)
    #lock.release()

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

        #lock.acquire()
        DMO = file.readlines()
        file.close()
        #lock.release()

    # initializing /DeclareMathOperator dictionary
    keyword_dict={}
    for i in DMO:
        ibegin, iend = i.find('{'), i.find('}')
        keyword_dict[i[ibegin+1 : iend]] = i

    # Dealing with "Macros"
    Macro_file = os.path.join(path_to_folder, "Macros_paper.txt")
    with open(Macro_file, 'r') as file:

        #lock.acquire()
        Macro = file.readlines()
        file.close()
        #lock.release()

    # initializing /Macros dictionary
    keyword_Macro_dict={}
    for i in Macro:
        ibegin, iend = i.find('{'), i.find('}')
        keyword_Macro_dict[i[ibegin+1 : iend]] = i

    # Path to the folder containing Large and Small equations
    for Path in [LargeEqn_Path, SmallEqn_Path]:
        for File in os.listdir(Path):

            #lock.acquire()

            main_file = os.path.join(Path, File)
            
            #lock.acquire()
            #print(main_file)
            #lock.release()
            
            with open (main_file, 'r') as FILE:
                #lock.acquire()
                eqn = FILE.readlines()
                FILE.close()
                #lock.release()
                
            TeX_name = File.split(".")[0]
            # calling function to create tex doc for the particular folder --> giving all latex eqns, DMOs, Macros and tex_folder path as arguments
            if len(eqn)!=0:
                if Path == LargeEqn_Path:
                    CreateTexDoc(eqn[0], keyword_dict, keyword_Macro_dict, TexFolder_Large_Eqn, TeX_name)
                else:
                    CreateTexDoc(eqn[0], keyword_dict, keyword_Macro_dict, TexFolder_Small_Eqn, TeX_name)
            
            #lock.release()


if __name__ == "__main__":

    for DIR in args.directories:

      print('DIR:  ', DIR)
      DIR = str(DIR)
      year = str(args.year)

      # paths
      src_path = args.source
      base_dir = os.path.join(src_path, f'{year}/{DIR}')

      # Latex_equations directory
      latex_equations = os.path.join(base_dir, "latex_equations")

      # tex_files dumping directory
      tex_files = os.path.join(base_dir, "tex_files")
      if not os.path.exists(tex_files):
          subprocess.call(['mkdir', tex_files])

      '''
      # loop through the folders
      temp = []

      for folder in os.listdir(latex_equations):

          temp.append([folder, tex_files])

      with Pool(multiprocessing.cpu_count()-12) as pool:
          pool.map(main, temp)
      '''
      for folder in os.listdir(latex_equations): 
          main([folder, tex_files])

# Printing stopping time
print('Stopping at:  ', datetime.now())
