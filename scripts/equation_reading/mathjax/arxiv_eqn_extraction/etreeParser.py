
import xml.etree.ElementTree as ET
import subprocess, os
import sys 
import xml.dom.minidom
import argparse
import multiprocessing
import logging 

from xml.etree.ElementTree import ElementTree
from datetime import datetime
from multiprocessing import Pool, Lock, TimeoutError


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
logging.basicConfig(filename = os.path.join(logFile_dst, f'{begin_month}-{end_month}_etree.log'),
                    level = logging.DEBUG, 
                    format = Log_Format, 
                    filemode = 'w')

logger = logging.getLogger()

# Printing starting time
print(' ')
start_time = datetime.now()
print('Starting at:  ', start_time)


# Defining lock
lock = Lock()

# Creating 'etree' directory 
for directory in args.directories:

    etree_path = f'{args.source}/{str(args.year)}/{str(directory)}/etree'
    
    if not os.path.exists(etree_path):
        subprocess.call(['mkdir', etree_path])
        
        
def main(DIR):    
    
    Mathml_path = f'{args.source}/{str(args.year)}/{DIR}/Simplified_mml'
    
    args_array = pooling(Mathml_path)
    
    with Pool(multiprocessing.cpu_count()-10) as pool:
        result = pool.map(etree, args_array)
    
    
def pooling(Mathml_path):
    
    temp = []
    
    for subDIR in os.listdir(Mathml_path):    
        
        subDIR_path = os.path.join(Mathml_path, subDIR)
        temp.append([subDIR, subDIR_path])
    
    return temp

def etree(args_array):
    
    global etree_path
    global lock
    
    # Unpacking the args array
    (subDIR, subDIR_path) = args_array 
    
    for tyf in ['Large_MML', 'Small_MML']:
    
        tyf_path = os.path.join(subDIR_path, tyf)
        
        # create folders
        Create_Folders(subDIR, tyf)
        
        for FILE in os.listdir(tyf_path):\
            
            try:
                FILE_path = os.path.join(tyf_path, FILE)
                
                FILE_name = FILE.split('.')[0]
                
                # converting text file to xml formatted file
                tree1 = ElementTree()
                
                lock.acquire()
                #print(FILE_path)
                lock.release()
                
                tree1.parse(FILE_path)
                sample_path = f'/projects/temporary/automates/er/gaurav/sample_etree/{FILE_name}_sample.xml'
                tree1.write(sample_path)
                
                # Writing etree for the xml files    
                tree = ET.parse(sample_path)
                xml_data = tree.getroot()
                xmlstr = ET.tostring(xml_data, encoding='utf-8', method='xml')
                input_string=xml.dom.minidom.parseString(xmlstr)
                xmlstr = input_string.toprettyxml()
                xmlstr= os.linesep.join([s for s in xmlstr.splitlines() if s.strip()]) # remove the weird newline issue
                
                result_path = os.path.join(etree_path, f'{subDIR}/{tyf}/{FILE_name}.xml')
                
                with open(result_path, "wb") as file_out:
                    file_out.write(xmlstr.encode(sys.stdout.encoding, errors='replace'))
            
            except: logger.warning(f'{FILE_path} not working.')
                
def Create_Folders(subDIR, tyf):
    
    global etree_path
    
    etree_subDIR_path = os.path.join(etree_path, subDIR) 
    etree_tyf_path = os.path.join(etree_subDIR_path, tyf)
    
    for F in [etree_subDIR_path, etree_tyf_path]:
        if not os.path.exists(F):
            subprocess.call(['mkdir', F]) 
            

if __name__ == "__main__":
    
    for DIR in args.directories:
        
        print(DIR)
        main(str(DIR))
        
    
    # Printing stoping time
    print(' ')
    stop_time = datetime.now()
    print('Stoping at:  ', stop_time)
    print(' ')
    print('etree writing process -- completed.')

