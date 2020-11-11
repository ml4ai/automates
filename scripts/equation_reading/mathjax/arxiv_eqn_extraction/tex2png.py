
# TeX file to pdf converter

import os, subprocess, random
import logging
import json
import multiprocessing
import time

from multiprocessing import Pool, Lock, TimeoutError
from threading import Timer
from pdf2image import convert_from_path


# Defining global lock 
lock = Lock()

# Setting up Logger - To get log files
Log_Format = '%(levelname)s:%(message)s'

logging.basicConfig(filename = 'tex2png.log', 
                    level = logging.DEBUG, 
                    format = Log_Format, 
                    filemode = 'w')

logger = logging.getLogger()


# Function to kill process if TimeoutError occurs
kill = lambda process: process.kill()

# Function to convert PDFs to PNGs
def pdf2png(folder, pdf_file, png_name, PNG_dst):
    
    global lock 
    #print(pdf_file)
    os.chdir(PNG_dst)
    
    #print(os.path.join(PNG_dst, pdf_file))
    
    try:
        
        command_args = ['convert','-background', 'white', '-alpha','remove', '-alpha', 'off',
                        '-density', '200','-quality', '100',pdf_file, f'{PNG_dst}/{png_name}.png']
        
        subprocess.Popen(command_args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        
        
        #convert_from_path(os.path.join(PNG_dst, pdf_file), fmt = 'png', output_folder = PNG_dst, output_file=f'{png_name}.png')
        
        # Removing pdf, log and aux file if exist
        
        #os.remove(f'{pdf_file.split(".")[0]}.pdf')
        os.remove(f'{pdf_file.split(".")[0]}.log')      
        try:  
            os.remove(f'{pdf_file.split(".")[0]}.aux')
        except:
            pass
        
        
            #lock.acquire()              
            #print(f'{pdf_file.split(".")[0]}.aux doesn\'t exists.')
            #lock.release()
                  
    except:
    
        lock.acquire()
        print(f"OOPS!!... This {folder}:{PNG_dst}:{pdf_file} file couldn't convert to png.")
        lock.release()
                  
# This function will run pdflatex
def run_pdflatex(run_pdflatex_list):
    
    global lock
    
    (folder, type_of_folder, texfile, PDF_dst) = run_pdflatex_list
    
    lock.acquire()
    #print(" ========== Currently running ==========")
    #print(f"{folder}:{type_of_folder}:{texfile}")
    lock.release()
    
    os.chdir(PDF_dst)
    command = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', os.path.join(type_of_folder,texfile)]
    
    #try:
    output = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    #stdout, stderr = output.communicate(timeout=5)
    my_timer = Timer(5, kill, [output])
    
    try:
        my_timer.start()
        stdout, stderr = output.communicate()
     
        #lock.acquire()
        #print(" ============= " * 25)
        #print(stdout)
        #lock.release()
        
        # Calling pdf2png
        pdf2png(folder, f'{texfile.split(".")[0]}.pdf', texfile.split(".")[0], PDF_dst)
    
    finally:
        my_timer.cancel()
    #except TimeoutError:
    #    lock.acquire()
    #    print(f"{folder}:{type_of_folder}:{texfile} --> Took more than 5 seconds to run.")
    #    lock.release()
        

def main(path):
    
    global lock
        
    # Folder path to TeX files
    TexFolderPath = os.path.join(path, "tex_files")
    #folder = "1402.1282"
    for folder in os.listdir(TexFolderPath):
        
        # make results PNG directories
        pdf_dst_root = os.path.join(path, f"latex_images/{folder}")
        PDF_Large = os.path.join(pdf_dst_root, "Large_eqns")
        PDF_Small = os.path.join(pdf_dst_root, "Small_eqns")
        for F in [pdf_dst_root, PDF_Large, PDF_Small]:
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
                
            with Pool(multiprocessing.cpu_count()-15) as pool:
                result = pool.map(run_pdflatex, temp)
        
if __name__ == "__main__":
    
    #for dir in ["1402", "1403", "1404", "1405"]:
    #    print(dir)
    dir = "1402"
    path = f'/xdisk/claytonm/projects/automates/er/gaurav/{DIR}'
    main(path)
