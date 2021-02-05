import os, glob

match = 0
total_SLE_MML = 0
SLE_count=0

SLE = '/projects/temporary/automates/er/gaurav/2014/1401/SLE/single_line_equation/*'
SLE_MML = '/projects/temporary/automates/er/gaurav/2014/1401/SLE/SLE_Mathjax_mml'
MML = '/projects/temporary/automates/er/gaurav/2014/1401/Mathjax_mml'

for folder in glob.glob(SLE):
    for tyf in glob.glob(os.path.join(folder, '*')):
        for  _ in glob.glob(os.path.join(tyf, '*')):
            SLE_count +=1

for folder in os.listdir(SLE_MML):
    for tyf in os.listdir(os.path.join(SLE_MML, folder)):
        for file_name in os.listdir(os.path.join(SLE_MML, f'{folder}/{tyf}')):            
            total_SLE_MML+=1
            try:
                F1 = open(os.path.join(SLE_MML, f'{folder}/{tyf}/{file_name}'),'r').readlines()[0]
                print(os.path.join(MML, f'{folder}/{tyf}/{file_name}'))
                print(F1)
                F2 = open(os.path.join(MML, f'{folder}/{tyf}/{file_name}'), 'r').readlines()[0]
                print(os.path.join(MML, f'{folder}/{tyf}/{file_name}'))
                print(F2)

                if F1==F2: match+=1
            except:pass

print('Total SLEs:  ', SLE_count)
print('Total SLE MMLs:  ', total_SLE_MML)
print('Total matches:   ', match)
print('matching %age:  ', (match/total_SLE_MML)*100)
