
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
args = parser.parse_args()

# Setting up Logger - To get log files
Log_Format = '%(levelname)s:%(message)s'
logFile_dst = os.path.join(args.source, f'{str(args.year)}/SLE_Logs')
begin_month, end_month = str(args.directories[0]), str(args.directories[-1])
logging.basicConfig(filename = os.path.join(logFile_dst, f'{begin_month}_{end_month}_MathJax_MML_SLE.log'),
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
        single_line_equations = os.path.join(root, "SLE/single_line_equations")

        # Path to directory contain MathML eqns
        mml_dir = os.path.join(root, "SLE/SLE_Mathjax_mml")

        if not os.path.exists(mml_dir):
            subprocess.call(['mkdir', mml_dir])

        MML_folder_list = os.listdir(mml_dir)
        
        temp = []

        for folder in os.listdir(single_line_equations):
            if folder not in MML_folder_list:
            #if folder == '1401.3751':
                temp.append([os.path.join(single_line_equations, folder), folder, mml_dir])

        print('temp done!')
        with Pool(multiprocessing.cpu_count()-10) as pool:
            result = pool.map(MjxMML, temp)


def MjxMML(l):

    global lock

    SLE_folder_path, folder, mml_dir = l
    
    #lock.acquire()
    #print(folder)
    #lock.release()

    for SLE_tyf in os.listdir(SLE_folder_path):
        tyf_mml = 'Small_MML' if SLE_tyf == 'Small_eqns' else 'Large_MML'
        SLE_mml_folder_path = os.path.join(mml_dir, folder)
        SLE_mml_tyf_path = os.path.join(SLE_mml_folder_path, tyf_mml)
        for F in [SLE_mml_folder_path, SLE_mml_tyf_path]:
            if not os.path.exists(F):
                os.makedirs(F)

        SLE_tyf_path = os.path.join(SLE_folder_path, SLE_tyf)
        for file_name in os.listdir(SLE_tyf_path):
            file_path =os.path.join(SLE_tyf_path, file_name)

            eqn = open(file_path, 'r').readlines()[0]
            
            lock.acquire()
            print(eqn)
            lock.release()

            # Define the webservice address
            webservice = "http://localhost:8081"

            # Translate and save each LaTeX string using the NodeJS service for MathJax
            res = requests.post(
                f"{webservice}/tex2mml",
                headers={"Content-type": "application/json"},
                json={"tex_src": json.dumps(eqn)},
                 )
            
            print(res.content)
            '''
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
            '''
            # Cleaning and Dumping the MathML strings to JSON file
            MML = CleaningMML(res.text)
            SLE_mml_file_path = os.path.join(SLE_mml_tyf_path, file_name)
            with open(SLE_mml_file_path, "w") as MML_output:
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
