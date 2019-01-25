import tokenize as tok
from io import BytesIO
from os.path import join, isfile
import inspect
import random
import pickle
import sys
import re

from nltk.tokenize import word_tokenize
from tqdm import tqdm


def clean_identifier(identifier):
    if "_" in identifier:
        case_split = identifier.split("_")
    else:
        # If the identifier is an all uppercase acronym (like `WMA`) then we
        # need to capture that. But we also the case where the first two letters
        # are capitals but the first letter does not belong with the second
        # (like `AVariable`). We also need to capture the case of an acronym
        # followed by a capital for the next word (like `AWSVars`).
        case_split = re.split("([A-Z]+|[A-Z]?[a-z]+)(?=[A-Z]|\b)", identifier)

    char_digit_split = list()
    for token in case_split:
        char_digit_split.extend(re.split("(\d+)", token))
    no_empty_tokens = [t for t in char_digit_split if t != ""]
    return ["<BoN>"] + no_empty_tokens + ["<EoN>"]


class CodeCrawler():
    def __init__(self, corpus_name="code-comment-corpus", modules=[]):
        self.name = corpus_name
        self.mods = modules
        self.functions = dict()
        self.code_comment_pairs = dict()
        self.clean_code_data = dict()

    def build_function_dict(self, outpath):
        filepath = join(outpath, "code.pkl")
        if isfile(filepath):
            self.functions = pickle.load(open(filepath, "rb"))
            return

        def find_functions_from_object(obj, expanded):
            results = list()
            try:
                components = inspect.getmembers(obj)
                for _, comp in components:
                    if inspect.isfunction(comp) or inspect.ismethod(comp):
                        results.append(comp)
                        # results.extend(find_functions_from_callable(comp))
                    elif inspect.ismodule(comp) and obj.__name__ in comp.__name__:
                        if comp.__name__ not in expanded:
                            expanded.append(comp.__name__)
                            results.extend(find_functions_from_object(comp, expanded))
                    elif inspect.isclass(comp):     # and obj.__name__ in comp.__name__:
                        if comp.__name__ not in expanded:
                            expanded.append(comp.__name__)
                            results.extend(find_functions_from_class(comp, expanded))
            except ModuleNotFoundError as e:
                print(e, file=sys.stderr)
            except AttributeError as e:
                print(e, file=sys.stderr)
            return results

        def find_functions_from_module(mod, expanded):
            """Returns a list of all functions from cur_module"""
            results = list()
            components = inspect.getmembers(mod)
            for _, comp in tqdm(components, desc="Searching {}".format(mod.__name__)):
                if inspect.isfunction(comp) or inspect.ismethod(comp):
                    results.append(comp)
                    # results.extend(find_functions_from_callable(comp))
                elif inspect.ismodule(comp) and mod.__name__ in comp.__name__:
                    expanded.append(comp.__name__)
                    results.extend(find_functions_from_object(comp, expanded))
                elif inspect.isclass(comp):     # and cur_module.__name__ in comp.__name__:
                    expanded.append(comp.__name__)
                    results.extend(find_functions_from_class(comp, expanded))
            return results

        def find_functions_from_class(cls, expanded):
            """Returns a list of all functions from cur_module"""
            results = list()
            try:
                components = inspect.getmembers(cls)
                for _, comp in components:
                    if inspect.isfunction(comp) or inspect.ismethod(comp):
                        results.append(comp)
                        # results.extend(find_functions_from_callable(comp))
            except ModuleNotFoundError as e:
                print(e, file=sys.stderr)
            except TypeError as e:
                print(e, file=sys.stderr)
            return results

        def find_functions_from_callable(callable):
            """Returns a list of all functions from cur_module"""
            results = list()

            components = inspect.getmembers(callable)
            for _, comp in components:
                if inspect.isfunction(comp) or inspect.ismethod(comp):
                    results.append(comp)

            return results

        for mod in self.mods:
            funcs = find_functions_from_module(mod, [])
            for func in tqdm(funcs, desc="Sourcing {}".format(mod.__name__)):
                try:
                    if not func.__module__ == "builtins":
                        (_, line_num) = inspect.getsourcelines(func)
                        code = inspect.getsource(func)
                        self.functions[(func.__module__, line_num)] = code
                except AttributeError as e:
                    print(e)
                except Exception as e:
                    print("Failed to get {} from {}: {}".format(func.__name__, func.__module__, e), file=sys.stderr)

        pickle.dump(self.functions, open(filepath, "wb"))

    def build_code_comment_pairs(self, outpath):
        if not self.functions:
            raise RuntimeWarning("Function dataset has not been built!!")

        filepath = join(outpath, "{}.pkl".format(self.name))
        code_filepath = join(outpath, "clean_code_data.pkl")
        if isfile(filepath):
            self.code_comment_pairs = pickle.load(open(filepath, "rb"))
            return

        num_docs = 0
        for idx, (identifier, code) in enumerate(tqdm(self.functions.items())):
            found_doc = False
            clean_code, clean_doc = list(), ""
            try:
                token_code = list(tok.tokenize(BytesIO(code.encode('utf-8')).readline))
                for tok_type, token, (line, _), _, full_line in token_code:
                    if tok_type == tok.COMMENT or tok_type == tok.ENCODING:
                        continue

                    if tok_type == tok.STRING and ("\"\"\"" in token or "'''" in token):
                        full_line = full_line.strip()
                        if full_line.endswith("'''") or full_line.endswith("\"\"\""):
                            for tok_type2, token2, (line2, _), _, full_line2 in token_code:
                                if line2 == line - 1 and "def" in full_line2:
                                    found_doc = True
                                    break
                                elif line2 >= line:
                                    break

                            if found_doc:
                                clean_token = token.strip("\"\"\"").strip("'''").strip("r\"\"\"").strip()

                                double_newline = clean_token.find("\n\n")
                                if double_newline > 1:
                                    clean_token = clean_token[:double_newline]

                                param_idx = clean_token.find("Parameters\n")
                                param_colon = clean_token.find("Parameters:\n")
                                arrow_idx = clean_token.find(">>>")
                                long_line = clean_token.find("----------\n")
                                example_colon = clean_token.find("Example::\n")
                                examples_colon = clean_token.find("Examples::\n")
                                refs_colon = clean_token.find("References::\n")
                                examples = clean_token.find("Examples\n")
                                example_Usage = clean_token.find("Example Usage:\n")
                                example_usage = clean_token.find("Example usage:\n")
                                requirements = clean_token.find("Requirements\n")
                                see_also_idx = clean_token.find("See Also\n")

                                indices = [s for s in [param_idx,
                                                       param_colon,
                                                       arrow_idx,
                                                       long_line,
                                                       example_colon,
                                                       examples,
                                                       examples_colon,
                                                       refs_colon,
                                                       example_usage,
                                                       example_Usage,
                                                       requirements,
                                                       see_also_idx] if s >= 0]
                                if len(indices) > 0:
                                    clean_doc += clean_token[:min(indices)]
                                else:
                                    clean_doc += clean_token

                                # if "----------" in clean_doc or "Example" in clean_doc:
                                #     print(clean_token)

                                clean_doc = clean_doc.strip()

                                if len(clean_doc) > 1:
                                    num_docs += 1
                                else:
                                    found_doc = False
                        else:
                            clean_code.append("<STRING>")
                    elif tok_type == tok.NEWLINE or tok_type == tok.NL:
                        clean_code.append("<NEWLINE>")
                    elif tok_type == tok.INDENT:
                        clean_code.append("<TAB>")
                    elif tok_type == tok.DEDENT:
                        clean_code.append("<UNTAB>")
                    elif tok_type == tok.ENDMARKER:
                        clean_code.append("<END>")
                    elif tok_type == tok.NUMBER:
                        clean_code.append("<NUMBER>")
                    elif tok_type == tok.STRING:
                        clean_code.append("<STRING>")
                    elif tok_type == tok.NAME:
                        identifier_sequence = clean_identifier(token)
                        clean_code.extend(identifier_sequence)
                    else:
                        clean_code.extend(token.split())

                self.clean_code_data[identifier] = clean_code
                if found_doc:
                    clean_doc = word_tokenize(clean_doc)

                    if len(clean_doc) > 5:
                        if clean_doc[5:].count(".") > 2:
                            first_period = clean_doc[5:].index(".") + 5
                            clean_doc = clean_doc[:first_period + 1]
                    if len(clean_code) <= 2000 and len(clean_doc) <= 110:
                        clean_code = ["<BoC>"] + clean_code + ["<EoC>"]
                        clean_doc = ["<BoL>"] + clean_doc + ["<EoL>"]
                        self.code_comment_pairs[identifier] = (clean_code, clean_doc)
            except tok.TokenError as e:
                print(e)

        pickle.dump(self.code_comment_pairs, open(filepath, "wb"))
        pickle.dump(self.clean_code_data, open(code_filepath, "wb"))

    def get_sentence_output(self, filepath):
        if not self.code_comment_pairs:
            raise RuntimeWarning("Code/comment dataset has not been built!!")

        outcode = join(filepath, "code-sentences.output")
        outcomm = join(filepath, "comm-sentences.output")
        outcodefull = join(filepath, "code-sentences-full.output")

        if isfile(outcode) and isfile(outcomm):
            return

        outcodefile = open(outcode, "w")
        outcommfile = open(outcomm, "w")
        outcodefullfile = open(outcodefull, "w")

        for code, comment in self.code_comment_pairs.values():
            outcodefile.write("{}\n".format(" ".join(code)))
            outcommfile.write("{}\n".format(" ".join(comment)))

        for code in self.clean_code_data.values():
            outcodefullfile.write("{}\n".format(" ".join(code)))

        outcodefile.close()
        outcommfile.close()
        outcodefullfile.close()

    def init_functions_from_file(self, filepath):
        self.functions = pickle.load(open(filepath), "rb")

    def init_code_comment_corpus_from_file(self, filepath):
        self.code_comment_pairs = pickle.load(open(filepath), "rb")

    def split_code_comment_data(self, filepath, train_size=0.8, val_size=0.15):
        if not self.code_comment_pairs:
            raise RuntimeWarning("Code/comment dataset has not been built!!")

        arr_data = list(self.code_comment_pairs.values())
        random.shuffle(arr_data)
        # total_length = len(arr_data)
        # train_length = int(train_size * total_length)
        # val_length = int(val_size * total_length) + train_length

        (test_code, test_comm) = map(list, zip(*arr_data[:802]))
        (val_code, val_comm) = map(list, zip(*arr_data[802: 1802]))
        (train_code, train_comm) = map(list, zip(*arr_data[1802:]))

        with open(join(filepath, "train.code"), "w") as outfile:
            for line in train_code:
                outfile.write("{}\n".format(" ".join(line)))

        with open(join(filepath, "train.nl"), "w") as outfile:
            for line in train_comm:
                outfile.write("{}\n".format(" ".join(line)))

        with open(join(filepath, "dev.code"), "w") as outfile:
            for line in val_code:
                outfile.write("{}\n".format(" ".join(line)))

        with open(join(filepath, "dev.nl"), "w") as outfile:
            for line in val_comm:
                outfile.write("{}\n".format(" ".join(line)))

        with open(join(filepath, "test.code"), "w") as outfile:
            for line in test_code:
                outfile.write("{}\n".format(" ".join(line)))

        with open(join(filepath, "test.nl"), "w") as outfile:
            for line in test_comm:
                outfile.write("{}\n".format(" ".join(line)))
