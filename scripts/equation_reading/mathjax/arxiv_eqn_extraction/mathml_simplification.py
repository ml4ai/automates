# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 21:24:26 2020

@author: gauravs
"""

import re
import subprocess, os
import multiprocessing
import argparse
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
Log_Format = '%(message)s'
logFile_dst = os.path.join(args.source, f'{str(args.year)}/Logs')
begin_month, end_month = str(args.directories[0]), str(args.directories[-1])
logging.basicConfig(filename = os.path.join(logFile_dst, f'{begin_month}-{end_month}_Unicode_MML.log'),
                    level = logging.DEBUG, 
                    format = Log_Format, 
                    filemode = 'w')

Unicode_logger = logging.getLogger()


def main():
    
    for DIR in args.directories:
        
        source_path = args.source
        year, DIR = str(args.year), str(DIR)
        
        print('Directory running:  ', DIR)
        
        DIR_path = os.path.join(source_path, f'{year}/{DIR}')
        MathJax_MML_path = os.path.join(DIR_path, 'Mathjax_mml')
        
        # Making new directory for Simplified MML
        Simp_MML_path = os.path.join(DIR_path, 'Simplified_mml')
        if not os.path.exists(Simp_MML_path):
            subprocess.call(['mkdir', Simp_MML_path])
        
        # Creating array fro pooling
        temp = []
        
        for folder in os.listdir(MathJax_MML_path):
            temp.append([os.path.join(MathJax_MML_path, folder), folder, Simp_MML_path])
        
        with Pool(multiprocessing.cpu_count()-30) as pool:
                result = pool.map(Simplification, temp)


def Simplification(pooling_list):
  
    global lock
    
    # Unpacking Pooling list of arguments
    (folder_path, folder, Simp_MML_path) = pooling_list
    
    # Making directory named <folder> in Simp_MML_path
    Simp_MML_folder_path = os.path.join(Simp_MML_path, folder)
    if not os.path.exists(Simp_MML_folder_path):
        subprocess.call(['mkdir', Simp_MML_folder_path])
    
    lock.acquire()
    #print('==+=='*20)
    #print(folder)
    lock.release()
    
    for type_of_folder in ['Large_MML', 'Small_MML']:
        
        type_of_folder_path = os.path.join(folder_path, type_of_folder)
        
        # Making directories in Simplified MML
        tyf_path = os.path.join(Simp_MML_folder_path, type_of_folder)
        if not os.path.exists(tyf_path):
            subprocess.call(['mkdir', tyf_path])
        
        for FILE in os.listdir(type_of_folder_path):
            
            MMLorg_LineList = open(os.path.join(type_of_folder_path, FILE), 'r').readlines()
            
            if len(MMLorg_LineList) > 0:
            
                MMLorg = MMLorg_LineList[0]
        
                if args.verbose:
                    lock.acquire()
                    # Printing original MML
                    print('Curently running folder:  ', folder)
                    print(' ')
                    print("=============== Printing original MML ================")
                    print('Original: \n')
                    print(MMLorg)
                    lock.release()
                    
                # Removing multiple backslashes
                i = MMLorg.find('\\\\')
                MMLorg = MMLorg.encode().decode('unicode_escape')
                
                while i >0:
                    MMLorg = MMLorg.replace('\\\\', '\\')
                    i = MMLorg.find('\\\\')
            
                    
                # Removing initial information about URL, display, and equation itself
                begin = MMLorg.find('<math')+len('<math')
                end = MMLorg.find('>')
                MMLorg = MMLorg.replace(MMLorg[begin:end], '')
                
                # Checking and logging Unicodes along with their asciii-code
                
                Unicode(MMLorg, os.path.join(type_of_folder_path, FILE))
                
                
                # ATTRIBUTES
                
                ## Attributes commonly used in MathML codes to represent equations
                ELEMENTS = ['mrow', 'mi', 'mn', 'mo', 'ms', 'mtext', 'math', 'mtable', 'mspace', 'maction', 'menclose', 
                              'merror', 'mfenced', 'mfrac', 'mglyph', 'mlabeledtr', 'mmultiscripts', 'mover', 'mroot',
                              'mpadded', 'mphantom', 'msqrt', 'mstyle', 'msub', 'msubsup', 'msup', 'mtd', 'mtr', 'munder',
                              'munderover', 'semantics']
                
                ## Attributes that can be removed
                Attr_tobeRemoved = ['class', 'id', 'style', 'href', 'mathbackground', 'mathcolor']
                
                ## Attributes that need to be checked before removing, if mentioned in code with their default value,
                ## will be removed else will keep it. This dictionary contains all the attributes with thier default values.
                Attr_tobeChecked = {
                                    'displaystyle':'false', 'mathsize':'normal', 'mathvariant':'normal','fence':'false',
                                    'accent':'false', 'movablelimits':'false', 'largeop':'false', 'stretchy':'false',
                                    'lquote':'&quot;', 'rquote':'&quot;', 'overflow':'linebreak', 'display':'block',
                                    'denomalign':'center', 'numalign':'center', 'align':'axis', 'rowalign':'baseline',
                                    'columnalign':'center', 'alignmentscope':'true', 'equalrows':'true', 'equalcolumns':'true',
                                    'groupalign':'{left}', 'linebreak':'auto', 'accentunder':'false'
                                   }
                
                                               
                MMLmod = Attribute_Definition(MMLorg, ELEMENTS, Attr_tobeRemoved, Attr_tobeChecked, os.path.join(type_of_folder_path, FILE))    
                 
                if args.verbose:
                    lock.acquire()
                    print("=============== Printing Modified MML ================")
                    print("Modified: \n")
                    print(MMLmod)   
                    lock.release()
                
                # Writing modified MML 
                tyf_path = os.path.join(Simp_MML_folder_path, type_of_folder)
                if not os.path.exists(tyf_path):
                    subprocess.call(['mkdir', tyf_path])
                    
                mod_FILE_path = os.path.join(tyf_path, FILE)
                with open(mod_FILE_path, 'w') as MMLmod_FILE:
                    MMLmod_FILE.write(MMLmod)
                    

def Unicode(MMLcode, running_path):
    
    global lock
    
    code_dict = {}
    
    symbol_index = [i for i,c in enumerate(MMLcode.split()) if ';<!--' in c and '&#x' in c]
    
    if args.verbose:
        lock.acquire()
        print(' ===+=== '*10)
        print('running_path:  ', running_path)
        lock.release()
    
    if len(symbol_index) != 0:
    
        for si in symbol_index:
            
            split_0 = MMLcode.split()[si]
            
            # grabbing part which has '#x<ascii-code>' in it.
            ind = [i for i, c in enumerate(split_0.split(';')) if '#x' in c]
            split_1 = split_0.split(";")[ind[0]]
            
            code = split_1.split('x')[1]
            
            ascii_code, Unicode = code, MMLcode.split()[si+1]
            
            lock.acquire()
            Unicode_logger.info(f'{running_path} -- {Unicode}:{ascii_code}')
            lock.release()
        
        
        # Printing final MML code
        if args.verbose:
            lock.acquire()
            print(f'{running_path} -- {Unicode}:{ascii_code}')
            lock.release()

# Removing unnecessary information or attributes having default values 
def Attribute_Definition(MMLcode, ELEMENTS, Attr_tobeRemoved, Attr_tobeChecked, running_path):
    
    global lock 
    
    # Defining array to keep Attribute definition
    Definition_array = []
    
    for ele in ELEMENTS:
        
        # Getting indices of the position of the element in the MML code
        position = [i for i in re.finditer(r'\b%s\b' % re.escape(ele), MMLcode)]
        
        
        for p in position:

            # Attribute begining and ending indices
            (Attr_begin, Attr_end) = p.span()
            
            # Length of the definition of the attribute
            Length = MMLcode[Attr_end:].find(">")   
        
            if Length >0:
                
                # Grabbing definition
                Definition = MMLcode[Attr_end: Attr_end+Length]
                
                if args.verbose:
                    lock.acquire()
                    print("MathML element:  ", ele)
                    print("Defnition:  ", Definition)
                    lock.release()
                    
                # Append unique definition
                if Definition not in Definition_array:
                    Definition_array.append(Definition)
    
    
    for Darr in Definition_array:
    
        if '=' in Darr:
        
        # Attribute and its value -- of the element 
            AttributeParameter = Darr.replace(" ", "").split("=")[0]
            AttributeValue = Darr.replace(" ", "").split("=")[1]
            
            # If Attribute has a defualt value, we can remove it
            # Checking which attributes can be removed
            if AttributeParameter not in Attr_tobeRemoved:
                
                if AttributeParameter in Attr_tobeChecked.keys():
                    
                    if AttributeValue.replace('\\','').replace('"', '') == Attr_tobeChecked[AttributeParameter]:
                        
                        MMLcode = MMLcode.replace(Darr, '')         
            else:
                MMLcode = MMLcode.replace(Darr, '')
    
    return MMLcode
    
    
if __name__ == '__main__':
    main()
            
    # Printing stoping time
    print(' ')
    stop_time = datetime.now()
    print('Stoping at:  ', stop_time)
    print(' ')
    print('MathML simplification has completed.')             
    
