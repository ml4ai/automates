import pickle

from tqdm import tqdm

import utils.utils as utils

code_path = utils.CODE_CORPUS / "corpus" / "clean_code_data.pkl"
code_data = pickle.load(open(code_path, "rb"))

code = [(name, code) for name, code in code_data.items()]
print("Sorting code")
code.sort(key=lambda tup: tup[1])
print("code is sorted")

list_of_dup_lists = list()
for idx, (name1, code1) in enumerate(tqdm(code, desc="Searcing")):
    if idx < len(code):
        dup_list = list()
        for (name2, code2) in code[idx + 1:]:
            codestr1 = " ".join(code1)
            codestr2 = " ".join(code2)
            if codestr1 == codestr2:
                dup_list.extend([name1, name2])
            else:
                break

        if len(dup_list) > 0:
            dup_list = list(set(dup_list))
            dup_list.sort(key=lambda tup: (len(tup[0]), tup[1], tup[0]))
            list_of_dup_lists.append(dup_list)


# with open("duplicate_keys.txt", "w") as outfile:
#     for n1, n2 in dup_keys:
#         outfile.write("{}\t{}\n".format(n1, n2))

print(len(code_data.keys()))
for dup_list in list_of_dup_lists:
    for key in dup_list[1:]:
        if key in code_data:
            del code_data[key]

print(len(code_data.keys()))
new_code_path = utils.CODE_CORPUS / "no-dups-clean_code_data.pkl"
pickle.dump(code_data, open(new_code_path, "wb"))
