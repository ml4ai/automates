
# CONVERT LaTeX EQUATION TO MathML CODE USING MathJax
import requests
import subprocess, os
import json
import argparse
import multiprocessing
import logging 

from datetime import datetime
from multiprocessing import Pool, Lock, TimeoutError


# Printing starting time
print(' ')
start_time = datetime.now()
print('Starting at:  ', start_time)

# Defining global lock
lock = Lock()

# Argument Parser
parser = argparse.ArgumentParser(description='Parsing LaTeX equations from arxiv source codes')
parser.add_argument('-src', '--source', type=str, metavar='', required=True, help='Source path to arxiv folder')
parser.add_argument('-dir', '--directories', nargs="+",type=int, metavar='', required=True, help='directories to run seperated by space')
parser.add_argument('-yr', '--year', type=int, metavar='', required=True, help='year of the directories')

group = parser.add_mutually_exclusive_group()
group.add_argument('-v', '--verbose', action='store_true', help='print verbose')
args = parser.parse_args()


# Setting up Logger - To get log files
Log_Format = '%(levelname)s:%(message)s'

logFile_dst = os.path.join(args.source, f'{str(args.year)}/Logs')
begin_month, end_month = str(args.directories[0]), str(args.directories[-1])
logging.basicConfig(filename = os.path.join(logFile_dst, f'{begin_month}_{end_month}_MathJax_MML_newLock.log'),
                    level = logging.DEBUG, 
                    format = Log_Format, 
                    filemode = 'w')

logger = logging.getLogger()


def main():
    
    for DIR in args.directories:
        
        src_path = args.source
        year, DIR = str(args.year), str(DIR)
        root = os.path.join(src_path, f'{year}/{DIR}')
        
        print('Currently running:  ',DIR)
            
        # Path to image directory
        folder_images = os.path.join(root, "latex_images")
        
        # Path to directory contain MathML eqns
        mml_dir = os.path.join(root, "Mathjax_mml")
        
        if not os.path.exists(mml_dir):
            subprocess.call(['mkdir', mml_dir])
       
        MML_folder_list = os.listdir(mml_dir)
        
        temp = []
        
        for folder in os.listdir(folder_images):
        
            if folder not in MML_folder_list: 
                
                # Creating Macros dictionary
                keyword_Macro_dict, keyword_dict = Creating_Macro_DMO_dictionaries(root, folder)
                temp.append([DIR, root, mml_dir, folder_images, folder, keyword_Macro_dict, keyword_dict])
         
        with Pool(multiprocessing.cpu_count()-10) as pool:
            result = pool.map(Creating_final_equations, temp)
                 
def Creating_Macro_DMO_dictionaries(root, folder):
    
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
    

def Creating_final_equations(args_list):
    
    global lock
    
    # Unpacking the args_list
    (DIR, root, mml_dir, folder_images, folder, keyword_Macro_dict, keyword_dict) = args_list
    
    # Creating folder for MathML codes for specific file
    mml_folder = os.path.join(mml_dir, folder)
    
    # Creating folder for Large and Small eqns
    Large_MML = os.path.join(mml_folder, "Large_MML")
    Small_MML = os.path.join(mml_folder, "Small_MML")
    for F in [mml_folder, Large_MML, Small_MML]:
        if not os.path.exists(F):
            subprocess.call(['mkdir', F])
    
    #Appending all the eqns of the folder/paper to Latex_strs_json 
    #along with their respective Macros and Declare Math Operator commands.
    
    # Creating array of final eqns
    Large_eqns = os.path.join(folder_images, f"{folder}/Large_eqns")
    Small_eqns = os.path.join(folder_images, f"{folder}/Small_eqns")
    
    for type_of_folder in [Large_eqns, Small_eqns]:
        
        for index, eqn in enumerate(os.listdir(type_of_folder)):
        
            if '.png' in eqn:
        
                try:
                    file_name = eqn.split("-")[0].split(".")[0] 

                    EqnsType = "Large_eqns" if type_of_folder == Large_eqns else "Small_eqns"
                    file_path = os.path.join(root, f"latex_equations/{folder}/{EqnsType}/{file_name}.txt")

                    final_eqn = ""

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

                    # Printing the final equation string
                    if args.verbose:
                        lock.acquire()
                        print("final equation is  ", final_eqn)
                        lock.release()

                    MML = Large_MML if type_of_folder == Large_eqns else Small_MML

                    MjxMML(file_name, folder, final_eqn, type_of_folder, MML)

                except:
                    lock.acquire()
                    if args.verbose:
                      print( " " )
                      print(f' {type_of_folder}/{file_name}: can not be converted.')
                      print( " =============================================================== " )

                    logger.warning(f'{type_of_folder}/{file_name}: can not be converted.')
                    lock.release()
                    
    
def MjxMML(file_name, folder, final_eqn, type_of_folder, mml_path):

    global lock
    
    # Define the webservice address
    webservice = "http://localhost:8081"
    # Load the LaTeX string data
    eqn=final_eqn
    
    # Translate and save each LaTeX string using the NodeJS service for MathJax
    res = requests.post(
        f"{webservice}/tex2mml",
        headers={"Content-type": "application/json"},
        json={"tex_src": json.dumps(eqn)},
         )
     
    if args.verbose:
        lock.acquire()
        print(f'Converting latex equation to MathML using MathJax webserver of {file_name}....')
        print(' ')
        print(f'Response of the webservice request: {res.text}')
        lock.release()
    
    # Capturing the keywords not supported by MathJax
    if "FAILED" in res.content.decode("utf-8"):
        # Just to check errors
        TeXParseError = res.content.decode("utf-8").split("::")[1]
        
        # Logging incorrect/ unsupported keywords along with their equations
        if "Undefined control sequence" in TeXParseError:
            Unsupported_Keyword = TeXParseError.split("\\")[-1]
            
            lock.acquire()
            if args.verbose:
                print(f'{type_of_folder}/{file_name}:{Unsupported_Keyword} is either not supported by MathJax or incorrectly written.')   
            
            logger.warning(f'{type_of_folder}/{file_name}:{Unsupported_Keyword} is either not supported by MathJax or incorrectly written.')
            lock.release()
            
        elif "TypeError: Cannot read property 'root' of undefined" in TeXParseError:
            lock.acquire()
            print(folder)
            logger.warning(f'{type_of_folder}/{file_name}:{TeXParseError} -- Math Processing Error: Maximum call stack size exceeded. Killing the process and server.')
            lock.release()
        
        # Logging errors other than unsupported keywords
        else:
            lock.acquire()
            if args.verbose:
                print(f'{type_of_folder}/{file_name}:{TeXParseError} is an error produced by MathJax webserver.')
            
            logger.warning(f'{type_of_folder}/{file_name}:{TeXParseError} is an error produced by MathJax webserver.')
            lock.release()
                
    else:
        # Cleaning and Dumping the MathML strings to JSON file
        MML = CleaningMML(res.text)
        
        if args.verbose:
            lock.acquire()
            print(f"writing {file_name}")
            lock.release()
        
        with open(os.path.join(mml_path, f"{file_name}.txt"), "w") as MML_output:
            MML_output.write(MML)
            MML_output.close()

def CleaningMML(res):

    # Removing "\ and /" at the begining and at the end
    res = res[res.find("<"):]
    res = res[::-1][res[::-1].find(">"):]
    res = res[::-1]
    
    # Removing "\\n"
    res = res.replace(">\\n", ">")
    return(res)       
    
    
if __name__ == "__main__":
    main()

    # Printing stoping time
    print(' ')
    stop_time = datetime.now()
    print('Stoping at:  ', stop_time)
    print(' ')
    print('LaTeX-MathML conversion has completed.')
