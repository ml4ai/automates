import os
import random
import json
import shutil
import subprocess

def main():

    # Defining paths
    mml_path = '/projects/temporary/automates/er/gaurav/2014/1401/SLE/SLE_Mathjax_mml'
    Sim_path = '/projects/temporary/automates/er/gaurav/2014/1401/SLE/SLE_Simplified_mml'
    png_path = '/projects/temporary/automates/er/gaurav/2014/1401/latex_images'
    latex_equation_path = '/projects/temporary/automates/er/gaurav/2014/1401/SLE/single_line_equations'

    # Generatingarrays of dictionaries of {source:mml} and {mml:simplified_mml}
    (MML_eqn_src, PNG_eqn_src) = ArrayGenerator(mml_path, Sim_path, png_path, latex_equation_path)

    # printing array of dictionaries
    print('Total number fo MML pairs:  ', len(MML_eqn_src))
    print('Total number fo latex_mml pairs:  ', len(PNG_eqn_src))

    # Destination paths
    destination1 = '/home/gauravs/Automates/SLE/mathml_data_dev.js'
    destination2 = '/home/gauravs/Automates/SLE/latex_data_dev.js'

    # converting json files to js files -- as required for html script for visualization
    json2js(MML_eqn_src, destination1, 'MML')
    json2js(PNG_eqn_src, destination2, 'PNG')

    # making zip folder of all the PNGs of respective latex equations
    shutil.make_archive('/home/gauravs/Random_PNG', 'zip', '/home/gauravs/Random_PNG')


def ArrayGenerator(mml_path, Sim_path, png_path, latex_equation_path):

    print('ArrayGenerator')
    i=0
    
    MML_eqn_src = []
    PNG_eqn_src = []

    for _ in range(10):

        # MML-Simplified MML arrays
        random_folder = random.choice([x for x in os.listdir(mml_path)])
        random_folder_path = os.path.join(mml_path, random_folder)
        print(random_folder_path)
        for tyf in os.listdir(random_folder_path):

            tyf_path = os.path.join(random_folder_path, tyf)

            for FILE in os.listdir(tyf_path):
                temp_dict, temp_dict2 = {}, {}

                FILE_path = os.path.join(tyf_path, FILE)
                print('FILE_path:  ', FILE_path)
                mml_eqn = open(FILE_path, 'r').readlines()[0]
                temp_dict['mml1'] = mml_eqn


                Sim_random_folder_path = os.path.join(Sim_path, random_folder)
                Sim_tyf_path = os.path.join(Sim_random_folder_path, tyf)
                Sim_FILE_path = os.path.join(Sim_tyf_path, FILE)

                Sim_eqn = open(Sim_FILE_path, 'r').readlines()[0]
                temp_dict['mml2'] = Sim_eqn
                MML_eqn_src.append(temp_dict)

                # PNG - MML arrays
                random_png_path = os.path.join(png_path, random_folder)

                tyf_ = 'Large_eqns' if tyf == 'Large_MML' else 'Small_eqns'

                tyf_png_path = os.path.join(png_path, f'{random_folder}/{tyf_}')
                tyf_LE_path = os.path.join(latex_equation_path, f'{random_folder}/{tyf_}')

                LEfile_path = os.path.join(tyf_LE_path, FILE)
                print('LEfile_path:  ', LEfile_path)
                LE_eqn = open(LEfile_path, 'r').readlines()[0]

                temp_dict2['src'] = LE_eqn
                temp_dict2['mml'] = mml_eqn

                PNG_eqn_src.append(temp_dict2)

                # Getting respective image
                png_file = os.path.join(tyf_png_path, f'{FILE.split(".")[0]}.png0001-1.png')
                print('png_file_path:  ', png_file)
                subprocess.call(['cp', png_file, f'/home/gauravs/Random_PNG/{i}.png'])
                i+=1

    return (MML_eqn_src, PNG_eqn_src)


# JSON to javascript converter
def json2js(json_data, output_file, Flag, var_name='eqn_src'):

    with open(output_file, 'w') as fout:
        fout.write(f'{var_name} = [\n')
        for i, datum in enumerate(json_data):
            fout.write('  {\n')
            #fout.write(f'    eqn_num: {repr(datum["eqn_num"])},\n')

            if Flag == 'PNG':
                fout.write(f'    src: {repr(datum["src"])},\n')
                fout.write(f'    mml: {repr(datum["mml"])}\n')
            else:
                fout.write(f'    mml1: {repr(datum["mml1"])},\n')
                fout.write(f'    mml2: {repr(datum["mml2"])}\n')

            fout.write('  }')
            if i < len(json_data):
                fout.write(',')
            fout.write('\n')
        fout.write('];')


if __name__ == '__main__':

    main()
