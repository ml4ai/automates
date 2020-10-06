# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 15:48:11 2020

@author: gaura

Unzipping tex files and combining preamble and main tex file
"""
import os
import json
from subprocess import call

# path to the directory having zip files
dir_zip =  "/home/gauravs/Automates/LaTeX_src"
zip_folder = os.path.join(dir_zip, "1401")
os.chdir(zip_folder)
#folder_dir = "/home/gauravs/Automates/LaTeX_src"

# reading the zip_files

for fldr in os.listdir(zip_folder):
    print(fldr)
    fldr_path = os.path.join(zip_folder, fldr)
    os.chdir(fldr_path)

#fldr_path = "/home/gauravs/Automates/LaTeX_src/1401/1401.3518"
# combining the preamble, bibtex, and main tex file --> reanme them main.tex
   # total number of tex files

    tex_files = [file for file in os.listdir() if '.tex' in file]
    
    if len(tex_files) > 1:
        
        files = {}
        # read all the tex files to know which one has \input or \import statement
        for tf in tex_files:                       
            # reading the tex file
            pathf = "path to tex file"
            with open(pathf) as TF:
                lines = TF.readlines()
            
            temp = []
            for line_index, line in enumerate(lines):
                if '\\input' in line:
                    # get the imported file name
                    if '{' in line:
                        imported_file = line[line.find('{')+1 : line.find('}')]
                    else:
                        imported_file = line[(line.find("\\input")+6):line.find('tex')+3 ].strip()

                    imported_file = imported_file.replace('\\n', '')

                    if '.tex' not in imported_file:
                        temp.append('{}.tex'.format(imported_file))
                    else:
                        temp.append(imported_file)

            files[tf] = temp
            
        # checking  if all files.values are [] --> ValueEmpty = True
        ValueEmpty = True
        for V in files.values():
            if V != []:
                ValueEmpty = False

         # if values are not empty --> ValueEmpty: False
        if not ValueEmpty:

            # Calling Files
            key_list = list(files.keys())
            # set of Imported files in each of the Calling Files arranged in the same order
            val_list = list(files.values())
            # all the imported files --> combined
            all_imported = []
            for vl in val_list:
                for v in vl:
                    if v not in all_imported:
                        all_imported.append(v)

            # extra list to keep track of remaining files after deleting the files
            rem_keys = key_list

          # before moving forward we need to remove unwanted files
          # i.e. files which are present in the folder as tex file but is neither
          # importing any file nor get imported to another.

            # get the keys whose values are empty --> not calling any other file
            useless_tex = []
            for chk_key in key_list:
                if files[chk_key] == [] and chk_key not in all_imported:
                    useless_tex.append(chk_key)

            # remove the useless files from the files dictionary
            for useless in useless_tex:
                del files[useless]

            N = len(key_list)
            for keys in key_list:
                print("keys --> {}".format(keys))
                if N >1:
                # check the keys that has no values --> no file imported in this file
                    if files[keys] == []:
                        for key, value in files.items():
                            print("key --> {}".format(key))
                            print("value --> {}".format(value))
                            if keys in value:
                             # print([keys, key, value])
                                CallingFile = key
                                print(CallingFile)
                     # open CallingFile and replace the "\input{keys}" --> entire file (as list)
                        os.chdir(fldr_path)
                        pathCF = os.path.join(fldr_path, CallingFile)
                        pathK = os.path.join(fldr_path, keys)
                        with open(pathCF, 'r') as CF:
                            CFlines = CF.readlines()
                        with open(pathK, 'r') as K:
                            Klines = K.readlines()

                        for CFl_index, CFl in enumerate(CFlines):
                            if "\input" in CFl:
                                if CFl[CFl.find('{')+1 : CFl.find('}')] == keys:
                                   CFlines = [CFl.replace(CFl, Klines) for CFLines_index, CFL in enumerate(CFlines) if CFLines_index == CFl_index]

                        # re-writing the opened CallingFile
                        os.chdir(fldr_path)
                        with open(CallingFile, 'w') as CF:
                            json.dump(CFlines, CF, indent=4)

                        # remove the imported file from the files dictionary
                        # also remove it from the values of the file it is imported to
                        del files[keys]
                        old_value = files[CallingFile]
                        new_value = [i for i in old_value if i != keys]
                        files[CallingFile] = new_value
                    N-=1

            # re-writing the main file --> expanding all the list
            main_new = []
            with open (rem_keys[0], 'r') as main:
                main_new_lines = main.readlines()
            for mnl in main_new_lines:
                if type(mnl) == list:
                    for l in mnl:
                        main_new.append(mnl)
                else:
                    main_new.append(mnl)

            os.chdir(fldr_path)
            with open("main_new.tex", 'w') as main:
                json.dump(main_new, main, indent=4)

    # files.values() are [] --> empty
        else:
            os.chdir(fldr_path)
            main_new = []
            for K in files.keys():
                with open (K,'r') as main:
                     klines_ValueEmpty = main.readlines()
                for klVE in  klines_ValueEmpty:
                    main_new.append(klVE)

  # if there are only one tex file
    else:
    # rename the only tex file as main.tex
        src, dst = tex_files[0], 'main_new.tex'
        os.rename(src, dst)


