# -*- coding: utf-8 -*-
import os, glob, json

def main():

    MML = '/projects/temporary/automates/er/gaurav/2014/1401/Simplified_mml/*'

    tokens=[]
    F = open('/projects/temporary/automates/er/gaurav/MML_tokens.txt', 'w') 

    for folder in glob.glob(MML):
        Path1 = os.path.join(MML, folder)
        print('------------'*5)
        print(os.path.basename(Path1))
        for tyf in glob.glob(os.path.join(Path1, '*')):
            Path2=os.path.join(Path1, tyf)
            for file in glob.glob(os.path.join(Path2, '*')):
                eqn = open(file, 'r').readlines()[0]

                open_angle = [idx_open for idx_open, angle in enumerate(eqn) if angle == '<']
                close_angle = [idx_close for idx_close, angle in enumerate(eqn) if angle == '>']

                for i in range(len(open_angle)):
                    token1 = eqn[open_angle[i]:close_angle[i]+1]
                    if token1 not in tokens:
                        F.write(f'{token1}\n')
                        if i<len(open_angle)-1:
                            token2 = eqn[close_angle[i]+1:open_angle[i+1]]
                            token2=token2.strip()
                            if token2 not in tokens:
                                F.write(f'{token2}\n')
                

if __name__=='__main()':
    main()
    print('Job Done!')
