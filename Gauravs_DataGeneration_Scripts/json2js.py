# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 00:36:21 2020

@author: gaura

JSON to javascript converter
"""
def json2js(json_data, output_file, var_name='eqn_src'):
    
    with open(output_file, 'w') as fout:
        fout.write(f'{var_name} = [\n')
        for i, datum in enumerate(json_data):
            fout.write('  {\n')
            fout.write(f'    src: {repr(datum["src"])},\n')
            fout.write(f'    mml: {repr(datum["mml"])}\n')
            fout.write('  }')
            if i < len(json_data):
                fout.write(',')
            fout.write('\n')
    fout.write('];')
            
            
source = r'C:\Users\gaura\OneDrive\Desktop\AutoMATES\REPO\results_file\src_mml_array.txt'
destination = r'C:\Users\gaura\OneDrive\Desktop\AutoMATES\REPO\results_file\src_mml_js.js'

if __name__ == '__main__':
    json2js(source, destination)
    
