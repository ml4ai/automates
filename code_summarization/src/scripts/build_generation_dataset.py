import csv
import random
from tqdm import tqdm

import utils.utils as utils

code = utils.CODE_CORPUS / "corpus" / "code-sentences.txt"
comm = utils.CODE_CORPUS / "corpus" / "comm-sentences.txt"
gen_path = utils.CODE_CORPUS / "input" / "generation_dataset.tsv"


codefile = open(code, "r")
commfile = open(comm, "r")

data = list()
for code_line, comm_line in tqdm(zip(codefile.readlines(), commfile.readlines())):
    code_line = code_line.strip()
    comm_line = comm_line.strip()
    stripped = (c for c in comm_line if ord(c) < 128)
    stripped_code = (c for c in code_line if ord(c) < 128)
    data.append(("".join(stripped_code), "".join(stripped)))

codefile.close()
commfile.close()

random.shuffle(data)

outfile = open(gen_path, 'wt')
tsv_writer = csv.writer(outfile, delimiter='\t')
tsv_writer.writerows(data)
outfile.close()
