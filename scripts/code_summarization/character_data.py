import utils.utils as utils


def get_char_list(words):
    chars = list()
    for word in words:
        if word.startswith("<") and word.endswith(">"):
            chars.append(word)
        else:
            chars.extend(list(word))

        if not (word == "<EoC>" or word == "<EoL>"):
            chars.append("<S>")
    return chars


def words_to_chars(in_filename, out_filename):
    with open(in_filename, "r+") as infile:
        with open(out_filename, "w+") as outfile:
            for line in infile:
                chars = list()
                words = line.split()
                if "" in words:
                    print("PROBLEM:\n\t{}".format(words))
                for word in words:
                    if word.startswith("<") and word.endswith(">"):
                        chars.append(word)
                    else:
                        chars.extend(list(word))

                    if not (word == "<EoC>" or word == "<EoL>"):
                        chars.append("<S>")
                if "" in chars:
                    print("PROBLEM:\n\t{}\n\t{}".format(chars, words))
                outfile.write(" ".join(chars) + "\n")


code_data_file = utils.CODE_CORPUS / "corpus" / "code-sentences-full.txt"
comm_data_file = utils.CODE_CORPUS / "corpus" / "comm-sentences.txt"

code_char_file = utils.CODE_CORPUS / "corpus" / "code-char-sentences-full.txt"
comm_char_file = utils.CODE_CORPUS / "corpus" / "comm-char-sentences.txt"

words_to_chars(code_data_file, code_char_file)
words_to_chars(comm_data_file, comm_char_file)
