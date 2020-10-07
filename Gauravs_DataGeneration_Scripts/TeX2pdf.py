# pdf and png
import os, subprocess
import json
from shutil import copyfile
from func_timeout import func_timeout, FunctionTimedOut

# for creating pdf files 
def run_pdflatex(tf, texfile):
    command = ['pdflatex','-interaction=batchmode', 'nonstopmode',os.path.join(tf,texfile)]
    output = subprocess.run(command)
    return output

def main(path):
    # To collect the incorrect or not working PDFs logs
    IncorrectPDF_LargeEqn, IncorrectPDF_SmallEqn = {}, {}
    
    # Folder path to TeX files
    TexFolderPath = os.path.join(path, "tex_files")
    
    for folder in os.listdir(TexFolderPath):
        # make latex_correct_eqn folders
        latex_correct_equations_folder = os.path.join(path, f"latex_correct_equations/{folder}")
        latex_correct_equations_folder_Large = os.path.join(latex_correct_equations_folder, "Large_eqns")
        latex_correct_equations_folder_Small = os.path.join(latex_correct_equations_folder, "Small_eqns")
        for F in [latex_correct_equations_folder, latex_correct_equations_folder_Large, latex_correct_equations_folder_Small]:
            if not os.path.exists(F):
                subprocess.call(['mkdir',F])

        # make results PDF directory
        eqn_tex_dst_root = os.path.join(path, f"latex_pdf/{folder}")
        PDF_Large = os.path.join(eqn_tex_dst_root, "Large_eqns_PDFs")
        PDF_Small = os.path.join(eqn_tex_dst_root, "Small_eqns_PDFs")
        for F in [eqn_tex_dst_root, PDF_Large, PDF_Small]:
            if not os.path.exists(F):
                subprocess.call(['mkdir', F])
        
        # Paths to Large and Small TeX files
        Large_tex_files = os.path.join(TexFolderPath, f"{folder}/Large_eqns")
        Small_tex_files = os.path.join(TexFolderPath, f"{folder}/Small_eqns")
        for tf in [Large_tex_files, Small_tex_files]: 
            for texfile in os.listdir(tf):
                i = texfile.split(".")[0]
                OutFlag = False
                try:
                    if tf == Large_tex_files:
                        os.chdir(PDF_Large)
                        output = func_timeout(5, run_pdflatex, args=(tf, texfile))
                        OutFlag = True
                        # Removing log file
                        os.remove(os.path.join(PDF_Large, f'{i}.log'))
                    else:
                        os.chdir(PDF_Small)
                        output = func_timeout(5, run_pdflatex, args=(tf, texfile))
                        OutFlag = True
                        # Removing log file
                        os.remove(os.path.join(PDF_Small, f'{i}.log'))

                except FunctionTimedOut:
                    print("%s couldn't run within 5 sec"%texfile)

                # copying the tex file to the correct latex eqn directory
                if OutFlag:
                    if output.returncode==0:
                        if tf == Large_tex_files:
                            copyfile(os.path.join(tf,texfile), os.path.join(os.path.join(latex_correct_equations_folder_Large, f"{texfile}")))
                        else:
                            copyfile(os.path.join(tf,texfile), os.path.join(os.path.join(latex_correct_equations_folder_Small, f"{texfile}")))
                    else:
                        try:
                            # Getting line number of the incorrect equation from Eqn_LineNum_dict dictionary got from ParsingLatex
                            # Due to dumping the dictionary in ParsingLatex.py code, we will treating the dictionary as text file.
                            Paper_Eqn_number = "{}_{}".format(folder, texfile.split(".")[0])  # Folder#_Eqn# --> e.g. 1401.0700_eqn98
                            Eqn_Num = "{}".format(texfile.split(".")[0])   # e.g. eqn98
                            Index = [i for i,c in enumerate(Eqn_LineNum[0].split(",")) if Eqn_Num in c] # Getting Index of item whose keys() has eqn#
                            Line_Num = Eqn_LineNum[0].split(",")[Index[0]].split(":")[1].strip() # Value() of above Keys()
                            if tf == Large_tex_files:
                                IncorrectPDF_LargeEqn[Paper_Eqn_number] = Line_Num
                            else:
                                IncorrectPDF_SmallEqn[Paper_Eqn_number] = Line_Num
                        except:
                            pass
                else:
                    try:
                        # If file couldn't execute within 5 seconds
                        Paper_Eqn_number = "{}_{}".format(folder, texfile.split(".")[0])
                        Eqn_Num = "{}".format(texfile.split(".")[0])
                        Index = [i for i,c in enumerate(Eqn_LineNum[0].split(",")) if Eqn_Num in c]
                        Line_Num = Eqn_LineNum[0].split(",")[Index[0]].split(":")[1].strip()
                        if tf == Large_tex_files:
                            IncorrectPDF_LargeEqn[Paper_Eqn_number] = Line_Num
                        else:
                            IncorrectPDF_SmallEqn[Paper_Eqn_number] = Line_Num
                    except:
                        pass

                try:
                    # Removing aux file if exist
                    os.remove(os.path.join(PDF_Large, f'{i}.aux')) if tf == Large_tex_files else os.remove(os.path.join(PDF_Small, f'{i}.aux'))
                except:
                    pass
    return(IncorrectPDF_LargeEqn, IncorrectPDF_SmallEqn)

if __name__ == "__main__":
    path = "/projects/temporary/automates/er/gaurav/results_file"
    IncorrectPDF_LargeEqn, IncorrectPDF_SmallEqn = main(path)
    # Dumping IncorrectPDF logs
    json.dump(IncorrectPDF_LargeEqn, open("/projects/temporary/automates/er/gaurav/results_file/IncorrectPDF_LargeEqn.txt","w"), indent = 4)
    json.dump(IncorrectPDF_SmallEqn, open("/projects/temporary/automates/er/gaurav/results_file/IncorrectPDF_SmallEqn.txt","w"), indent = 4)
