import pickle

import utils.utils as utils

code_path = utils.CODE_CORPUS / "corpus" / "code-comment-corpus.pkl"
code_data = pickle.load(open(code_path, "rb"))

code = [" ".join(code) for code, _ in code_data.values()]
function_sigs = list()
for code_str in code:
    def_idx = code_str.find(" def ")
    func_name_eoc = code_str.find("<EoN>", def_idx + 12)
    function_sigs.append(code_str[def_idx + 11: func_name_eoc + 5])

amount_caps = [sum([int(s.isupper()) for s in sig]) for sig in function_sigs]
amount_nums = [sum([int(s.isdigit()) for s in sig]) for sig in function_sigs]

data = list(zip(function_sigs, amount_caps, amount_nums))
data.sort(key=lambda tup: (tup[1], tup[2]), reverse=True)

(function_sigs, _, _) = map(list, zip(*data))

# function_sigs.sort(key=lambda el: len(el), reverse=True)
for sig in function_sigs[100:150]:
    print(sig)
    print("\n")
