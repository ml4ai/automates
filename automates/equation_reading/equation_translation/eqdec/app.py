import os
import shutil
import subprocess
from fastapi import FastAPI, File, UploadFile

app = FastAPI()

@app.get('/')
def index():
    return {'message': "It's alive!"}

@app.post('/decode_equation/')
def decode_equation(file: UploadFile = File(...)):
    """Gets an equation in an image and returns the sequence of latex tokens
    that would produce it."""
    model = '/home/eqdec/model.pt'
    src_dir = '/home/eqdec/images'
    src = '/home/eqdec/images.txt'
    output = '/home/eqdec/output.txt'
    image_path = os.path.join(src_dir, file.filename)
    # copy image to folder
    with open(image_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)
    # write name of image to translate
    with open(src, 'w') as f:
        print(file.filename, file=f)
    # build command
    cmd = ['python', '/home/eqdec/OpenNMT-py/translate.py',
        '-data_type', 'img',
        '-model', model,
        '-src_dir', src_dir,
        '-src', src,
        '-output', output,
        '-max_length', '150',
        '-beam_size', '5',
        '-image_channel_size', '1',
    ]
    # execute command
    res = subprocess.run(cmd, capture_output=True)
    # read results
    with open(output) as f:
        latex = f.read().strip()
    # delete image
    os.remove(image_path)
    # return results
    return {
        'filename': file.filename,
        'latex': latex,
    }
