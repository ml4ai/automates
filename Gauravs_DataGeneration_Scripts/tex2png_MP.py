# TeX file to pdf converter

import os, subprocess, random
import logging, pprint, traceback
import json
import multiprocessing
import timeout_decorator, signal
import time
import concurrent.futures as cf

from pebble import ProcessPool
from multiprocessing import Process, current_process, Pool, Lock, Value
from concurrent.futures import TimeoutError

logging.basicConfig(level=logging.DEBUG)
_L = logging.getLogger()

# Defining global lock 
lock = None
    
class JobTimeoutException(Exception):
    def __init__(self, jobstack=[]):
        super(JobTimeoutException, self).__init__()
        self.jobstack = jobstack
        
def timeout(timeout):
    """
    Return a decorator that raises a JobTimeoutException exception
    after timeout seconds, if the decorated function did not return.
    """

    def decorate(f):
        def timeout_handler(signum, frame):
            raise JobTimeoutException(traceback.format_stack())

        def new_f(*args, **kwargs):
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)

            result = f(*args, **kwargs)  # f() always returns, in this scheme

            signal.signal(signal.SIGALRM, old_handler)  # Old signal handler is restored
            signal.alarm(0)  # Alarm removed
            return result

        new_f.func_name = f.func_name
        return new_f

    return decorate
    
    
# for creating pdf files 
def run_pdflatex(list):
    
    global lock 
    
    type_of_folder = list[0]   # defined as tf in main()
    file_name = list[1]        # file_name to be converted
    PNG_dst = list[2]          # PNG directory to store PDFs, which in next step will be converted to PNGs
    
    os.chdir(PNG_dst)
    
    command_pdf = ['pdflatex','-interaction', 'nonstopmode',os.path.join(type_of_folder,file_name)]
    
    lock.acquire()
    #print(file_name)
    output = subprocess.run(command_pdf)
    lock.release()
    
    if output.returncode==0:  
        # Removing aux, log, and pdf files if exist
        try:
            os.remove(os.path.join(PNG_dst, f'{file_name.split(".")[0]}.log'))  
            os.remove(os.path.join(PNG_dst, f'{file_name.split(".")[0]}.aux'))
        except:
            pass
    else:
        try:
            os.remove(os.path.join(PNG_dst, f'{file_name.split(".")[0]}.log'))  
            os.remove(os.path.join(PNG_dst, f'{file_name.split(".")[0]}.pdf'))  
            os.remove(os.path.join(PNG_dst, f'{file_name.split(".")[0]}.aux'))
        except:
            pass
            
    return (file_name.split(".")[0])

def main(path):
    
    global lock 
    lock = Lock()                               # Global lock
    num_cores = multiprocessing.cpu_count()     # Total number of cores 
    cores_to_use = num_cores - 6                # Total no. of cores will be using
    p = Pool(cores_to_use)                      # Pooling cpu cores
    
    # To collect the incorrect or not working PDFs logs
    IncorrectPDF_LargeEqn, IncorrectPDF_SmallEqn = {}, {}
    
    # Folder path to TeX files
    TexFolderPath = os.path.join(path, "tex_files")
    folder="/projects/temporary/automates/er/gaurav/1402_results/tex_files/1402.0507"
    #for folder in os.listdir(TexFolderPath):
        
    # make results PNG directories
    #png_dst_root = os.path.join(path, f"latex_images/{folder}")
    png_dst_root = os.path.join(path, f"latex_images/1402.0507")
    PNG_Large = os.path.join(png_dst_root, "Large_eqns")
    PNG_Small = os.path.join(png_dst_root, "Small_eqns")
    for F in [png_dst_root, PNG_Large, PNG_Small]:
        if not os.path.exists(F):
            subprocess.call(['mkdir', F])
    
    # Paths to Large and Small TeX files
    #Large_tex_files = os.path.join(TexFolderPath, f"{folder}/Large_eqns")
    #Small_tex_files = os.path.join(TexFolderPath, f"{folder}/Small_eqns")
    Large_tex_files = os.path.join(folder, "Large_eqns")
    Small_tex_files = os.path.join(folder, "Small_eqns")

    for tf in [Large_tex_files, Small_tex_files]: 
        PNG_dst = PNG_Large if tf == Large_tex_files else PNG_Small
    
        # array to store pairs of [tf, each_file_in tf]
        # Will be used as arguments in pool.map            
        temp = []
        for TF in os.listdir(tf):
            temp.append([tf, TF, PNG_dst])
       
        # Mapping the tasks to pool of cores along with timer of 5sec
        with ProcessPool(max_workers = multiprocessing.cpu_count() - 6) as pool:
            future = pool.map(run_pdflatex, temp, timeout=5)
            iterator = future.result()
            
            #file.add_done_callback(task_done)
            running = True
            while running:
                try:
                    result = next(iterator)
                except StopIteration:
                    break   
                except TimeoutError as error:
                    print("function took longer than %d seconds" % error.args[1])
                    #break
                # Kill this process
        '''    
        with cf.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count() - 6) as executor:
            iterator = executor.map(run_pdflatex, temp)
            #for future in cf.as_completed(iterator, timeout=5):
            try:
                results = iterator.result(timeout=5)
    
            except cf.TimeoutError as timeout_error:
                print("Function is taking too long time")
                pass
            
        
        pool = multiprocessing.Pool(processes=34, maxtasksperchild=1)

        # Run the tasks unordered through the pool and give us an iterator
        result_iter = pool.map(run_pdflatex, temp, chunksize = 1)
        
        # Result collection object
        result_collection = []
        
        # Iterate through all the results
    
        while True:
            try:
                # if no timeout is set, Ctrl-C does weird things.
                result = result_iter.next(timeout=5)
                _L.info("Result received %s", result)
                result_collection.append(result)
            except JobTimeoutException as timeout_ex:
                _L.warning("Job timed out %s", timeout_ex)
                _L.warning("Stack trace:\n%s", ''.join(timeout_ex.jobstack))
                result_collection.append(None)
            except StopIteration:
                _L.info("All jobs complete!")
                break
            print(result)
        '''
        try:
            # Getting line number of the incorrect equation from Eqn_LineNum_dict dictionary got from ParsingLatex
            # Due to dumping the dictionary in ParsingLatex.py code, we will treating the dictionary as text file.
            Paper_Eqn_number = "{}_{}".format(folder, file)  # Folder#_Eqn# --> e.g. 1401.0700_eqn98
            Eqn_Num = "{}".format(file)   # e.g. eqn98
            Index = [i for i,c in enumerate(Eqn_LineNum[0].split(",")) if Eqn_Num in c] # Getting Index of item whose keys() has eqn#
            Line_Num = Eqn_LineNum[0].split(",")[Index[0]].split(":")[1].strip() # Value() of above Keys()
            if tf == Large_tex_files:
                IncorrectPDF_LargeEqn[Paper_Eqn_number] = Line_Num
            else:
                IncorrectPDF_SmallEqn[Paper_Eqn_number] = Line_Num
        except:
            pass
        
            
        #ProcessPool.close()
        #ProcessPool.join()
       
    return(IncorrectPDF_LargeEqn, IncorrectPDF_SmallEqn)

if __name__ == "__main__":
    
    #for dir in ["1402", "1403", "1404", "1405"]:
    dir = "1402"    
    print(dir)
    path = f"/projects/temporary/automates/er/gaurav/{dir}_results"
    IncorrectPDF_LargeEqn, IncorrectPDF_SmallEqn = main(path)
    # Dumping IncorrectPDF logs
    json.dump(IncorrectPDF_LargeEqn, open(os.path.join(path, "IncorrectPDF_LargeEqn.txt"),"w"), indent = 4)
    json.dump(IncorrectPDF_SmallEqn, open(os.path.join(path, "IncorrectPDF_SmallEqn.txt"),"w"), indent = 4)
