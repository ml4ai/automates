import os, subprocess, multiprocessing, glob, string

from datetime import datetime
from multiprocessing import Pool, Lock

print('Starting at:  ', datetime.now())

lower_set = string.ascii_lowercase

#for DIR in ['1401']:
def main():
    
    etree_path = '/projects/temporary/automates/er/gaurav/2014/1401/etree/*'
    single_line_equations = '/projects/temporary/automates/er/gaurav/2014/1401/single_line_equations'
    if not os.path.exists(single_line_equations):
        os.makedirs(single_line_equations)

    for folder_path in glob.glob(etree_path):
        SLE_folder_path = folder_path.replace('etree', 'single_line_equations')
        if not os.path.exists(SLE_folder_path):
            os.makedirs(SLE_folder_path)

        for tyf_path in glob.glob(os.path.join(folder_path, '*')):
            if 'Small_MML' in tyf_path:
                tyf = 'Small_MML'
                SLE_tyf = 'Small_eqns'
            else:
                tyf = 'Large_MML'
                SLE_tyf = 'Large_eqns'

            SLE_tyf_path = os.path.join(SLE_folder_path, SLE_tyf)
            if not os.path.exists(SLE_tyf_path):
                os.makedirs(SLE_tyf_path)

            temp=[]
            for etree_file in glob.glob(os.path.join(tyf_path, '*')):
                tex_file_path = etree_file.replace('etree', 'tex_files')
                tex_file_path = tex_file_path.replace(tyf, SLE_tyf)
                tex_file_path = tex_file_path.replace('.xml', '.tex')
                SLE_file_path = tex_file_path.replace('tex_files', 'single_line_equations')
                SLE_file_path = SLE_file_path.replace('.tex', '.txt')
                temp.append([tex_file_path, SLE_file_path])

            with Pool(multiprocessing.cpu_count()-10) as pool:
                pool.map(replacing_macros, temp)
    
    #tex_file_path='/projects/temporary/automates/er/gaurav/2014/1401/tex_files/1401.2692/Large_eqns/eqn46.tex'
    #SLE_file_path='/projects/temporary/automates/er/gaurav/2014/1401/single_line_equations/1401.2692/Large_eqns/eqn46.txt'
    #replacing_macros([tex_file_path, SLE_file_path])
    
def replacing_macros(l):

    tex_file_path, SLE_file_path = l

    eqn_parts = open(tex_file_path, 'r').readlines()
    begin, end = eqn_parts.index('\\begin{document}\n'), eqn_parts.index('\\end{document}')
    equation = ''
    for i in range(begin+1, end):
        equation += eqn_parts[i]

    macro_eqn = {}
    num_para = {}

    for part in eqn_parts:
        if 'newcommand' in part or 'renewcommand' in part:
            try:
                #temp=[]
                #print('  =====  '*10)
                #print(part)
                start, stop = part.find('{')+1, part.find('}')
                macro = part[start:stop]
                eqn_left = part[stop:]
                openBracket = [index for index, char in enumerate(eqn_left) if char == '{']
                closeBracket = [index for index, char in enumerate(eqn_left) if char == '}']
                expression = eqn_left[openBracket[0]+1:closeBracket[-1]]
                # check for any loose brackets
                ind, counter = 0, 0
                for i, char in enumerate(expression):
                    if char == '{':
                        counter+=1
                        ind=i
                    if char == '}':
                        counter-=1
                        ind=i

                if counter!=0: expression = expression.replace(expression[ind], '')

                if '#' not in expression:
                    macro_index = equation.find(macro)
                    macro_len = len(macro)
                    if equation[macro_index+macro_len] not in lower_set:
                        equation = equation.replace(macro, expression)

            except: pass
            '''
            temp.append(expression)
            if '#' in expression:
                openSquareBracket = [ind for ind, char in enumerate(eqn_left[stop:]) if char == '[']
                closeSquareBracket = [ind for ind, char in enumerate(eqn_left[stop:]) if char == ']']
                number_of_parameters = eqn_left[openSquareBracket[0]+1:closeSquareBracket[0]]
                temp.append(number_of_parameters)
            '''

    #print('The final equation is:  ',equation)
    equation=equation.replace('$\displaystyle', '')
    openCurlyBracket = [ind for  ind, char in enumerate(equation) if  char == '{']
    closeCurlyBracket = [ind for  ind, char in enumerate(equation) if  char == '}']
    if len(openCurlyBracket)==len(closeCurlyBracket):
        equation = equation[openCurlyBracket[1]+1:closeCurlyBracket[-2]]
    else:
        if len(openCurlyBracket)>len(closeCurlyBracket):
            equation = equation[openCurlyBracket[1]+1:]
        else: equation = equation[:closeCurlyBracket[-2]]

    if equation[-2:] == '\n':
        equation = equation[:-2]
    #print('The final equation is:  ',equation)
    with open(SLE_file_path, 'w') as FILE:
        FILE.write(equation)
        FILE.close()


if __name__=='__main__':
    main()
    print('Stopping at:  ', datetime.now())

