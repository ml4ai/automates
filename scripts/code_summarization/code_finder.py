import pickle
import random

from utils.utils import CODE_CORPUS


code_path = CODE_CORPUS / "corpus" / "code.pkl"
data = pickle.load(open(code_path, "rb"))

commented_funcs = list()
for key, code in data.items():
    if '"""' in code:
        commented_funcs.append(code)

random.shuffle(commented_funcs)
for func in commented_funcs[:20]:
    print(func)
