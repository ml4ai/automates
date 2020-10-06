# RENDERING .png FROM THE pdf FILES OF THE EQUATIONS

import os, subprocess
from pdf2image import convert_from_path

def main(pdf_file_path, pdf_file, Image_path):
    try:
        # extracting the image of the pdf
        output_file = '{}.png'.format(pdf_file.split(".")[0])
        convert_from_path(pdf_file_path, fmt = 'png', output_folder = Image_path, output_file=output_file)
    except:
        pass

if __name__ == "__main__":
    # Paths
    root = "/projects/temporary/automates/er/gaurav/results_file"
    pdf_path = os.path.join(root, "latex_pdf")
    image_path = os.path.join(root, "latex_images")
    
    for fldr in os.listdir(pdf_path):
        # Path to folder containing all pdf files of specific paper
        PDF_Large = os.path.join(pdf_path, f"{fldr}/Large_eqns_PDFs")
        PDF_Small = os.path.join(pdf_path, f"{fldr}/Small_eqns_PDFs")
        
        # mkdir image folder if not exists
        image_folder = os.path.join(image_path, fldr)
        image_folder_Large = os.path.join(image_folder, "Images_of_Large_Eqns")
        image_folder_Small = os.path.join(image_folder, "Images_of_Small_Eqns")
        for F in [image_folder, image_folder_Large, image_folder_Small]:
            if not os.path.exists(F):
                subprocess.call(["mkdir", F])
        
        # Looping through pdf files
        for pdf_folder in [PDF_Large, PDF_Small]:
            for pdf_file in os.listdir(pdf_folder):
                if pdf_file.split(".")[1] == "pdf":
                    if pdf_folder == PDF_Large:
                        pdf_file_path = os.path.join(PDF_Large, pdf_file) 
                        main(pdf_file_path, pdf_file, image_folder_Large)
                    else:
                        pdf_file_path = os.path.join(PDF_Small, pdf_file) 
                        main(pdf_file_path, pdf_file, image_folder_Small)
