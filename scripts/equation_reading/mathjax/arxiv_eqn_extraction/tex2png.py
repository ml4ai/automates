
# TeX file to pdf converter

import os, subprocess, random
import logging
import json
import multiprocessing
import argparse

from datetime import datetime
from multiprocessing import Pool, Lock, TimeoutError
from threading import Timer
from pdf2image import convert_from_path

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

logFile_dst = os.path.join(args.source, str(args.year))

logging.basicConfig(filename = os.path.join(logFile_dst, 'tex2png2016.log'),
                    level = logging.DEBUG, 
                    format = Log_Format, 
                    filemode = 'w')

logger = logging.getLogger()


# Function to kill process if TimeoutError occurs
kill = lambda process: process.kill()
#def Kill():
    
#    lambda process: process.kill()
    
#    if args.verbose:
#        lock.acquire()
#        print(f"{folder}:{type_of_folder}:{texfile} --> Took more than 5 seconds to run.")
#        lock.release()
    
#    logger.warning(f"{folder}:{type_of_folder}:{texfile} --> Took more than 5 seconds to run.")
    

# Function to convert PDFs to PNGs
def pdf2png(folder, pdf_file, png_name, PNG_dst, type_of_folder):
    
    global lock 
    
    os.chdir(PNG_dst)
    
    try:
        
        command_args = ['convert','-background', 'white', 
                        '-alpha', 'remove', 'off','-density', 
                        '200','-quality', '100',pdf_file, 
                        f'{PNG_dst}/{png_name}.png']
        
        subprocess.Popen(command_args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        
        # Removing log and aux file if exist
        
        os.remove(f'{pdf_file.split(".")[0]}.log')      
        
        try:  
            os.remove(f'{pdf_file.split(".")[0]}.aux')
        except:
            
            if args.verbose:
                lock.acquire()              
                print(f'{pdf_file.split(".")[0]}.aux doesn\'t exists.')
                lock.release()
                
            logger.warning(f'{folder}:{type_of_folder}:{pdf_file.split(".")[0]}.aux doesn\'t exists.')
                      
    except:
        
        if args.verbose:
            lock.acquire()
            print(f"OOPS!!... This {folder}:{PNG_dst}:{pdf_file} file couldn't convert to png.")
            lock.release()
        
        logger.warning(f"{folder}:{PNG_dst}:{pdf_file} file couldn't convert to png.")


# This function will run pdflatex
def run_pdflatex(run_pdflatex_list):
    
    global lock
    
    (folder, type_of_folder, texfile, PDF_dst) = run_pdflatex_list
    
    if args.verbose:
        lock.acquire()
        print(' ')
        print(f"Running --> {folder}:{type_of_folder}:{texfile}")
        lock.release()
    
    os.chdir(PDF_dst)
    command = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', os.path.join(type_of_folder,texfile)]
    
    output = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    
    # Kill the process if takes more than 5 seconds
    my_timer = Timer(5, kill, [output])
    #my_timer = Timer(5, Kill, [output])
    
    try:
        my_timer.start()
        stdout, stderr = output.communicate()
        
        if args.verbose:
            lock.acquire()
            print(' ')
            print('Subprocess Popen Output:  ', stdout)
            lock.release()
        
        # Calling pdf2png
        pdf2png(folder, f'{texfile.split(".")[0]}.pdf', texfile.split(".")[0], PDF_dst, type_of_folder)
    
    finally:
        my_timer.cancel()
    

def main(path):
    
    global lock
        
    # Folder path to TeX files
    TexFolderPath = os.path.join(path, "tex_files")
    
    for folder in os.listdir(TexFolderPath):
        
        if args.verbose:
            print("Folder:  ", folder)
        
        # make results PNG directories
        latex_images = os.path.join(path, 'latex_images')
        pdf_dst_root = os.path.join(latex_images, folder)
        PDF_Large = os.path.join(pdf_dst_root, "Large_eqns")
        PDF_Small = os.path.join(pdf_dst_root, "Small_eqns")
        for F in [latex_images, pdf_dst_root, PDF_Large, PDF_Small]:
            if not os.path.exists(F):
                subprocess.call(['mkdir', F])

        # Paths to Large and Small TeX files
        Large_tex_files = os.path.join(TexFolderPath, f"{folder}/Large_eqns")
        Small_tex_files = os.path.join(TexFolderPath, f"{folder}/Small_eqns")

        for type_of_folder in [Large_tex_files, Small_tex_files]: 
            PDF_dst = PDF_Large if type_of_folder == Large_tex_files else PDF_Small
        
            # array to store pairs of [type_of_folder, file in type_of_folder] Will be used as arguments in pool.map            
            temp = []
            for texfile in os.listdir(type_of_folder):
                temp.append([folder, type_of_folder, texfile, PDF_dst])
                
            with Pool(multiprocessing.cpu_count()-10) as pool:
                result = pool.map(run_pdflatex, temp)
        
if __name__ == "__main__":
    
    src_path = args.source
    year_path = os.path.join(src_path, str(args.year))    
    
    for DIR in args.directories:
        
        print(DIR)
        DIR = str(DIR)
        
        if args.verbose:
            print(" ==+== "*20)
            print('Directory:  ', DIR)
            
        #for path in os.listdir(os.path.join(year_path, DIR)):
        #    print(path)
        #    if '.log' not in path:
        main(os.path.join(year_path, DIR))
    
    # Printing stoping time
    print(' ')
    stop_time = datetime.now()
    print('Stoping at:  ', stop_time)
    print(' ')
    print('parsing latex equations completed.')
                
