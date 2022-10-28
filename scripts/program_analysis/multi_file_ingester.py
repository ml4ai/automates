import argparse
import glob

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='The path of source directory')

args = parser.parse_args()
path = args.path

files = glob.glob(path + '/**/*.py', recursive=True)
print(files)
#for subdir, dirs, files in os.walk(path):
#    for dir in dirs:
#        pass # Recurse into dir
#    for file in files:
#        pass # Check if source code file
