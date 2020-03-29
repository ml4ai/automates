import os
import json
import pprint
import src.equation_reading.equation_translation.img_translator as decode

IMG_SOURCE_ROOT = '/Users/claytonm/Google Drive/ASKE-AutoMATES/Data/Mini-SPAM/eqns/SPAM/PET/PETPT'

result_path = decode.png2latex(os.path.join(IMG_SOURCE_ROOT, '0.png'), IMG_SOURCE_ROOT)

print(result_path)

with open(result_path) as json_file:
    jeq = json.load(json_file)

pprint.pprint(jeq)

print(jeq['latex'])
