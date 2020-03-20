import tokenize as tok
from io import BytesIO
from os.path import isfile
import inspect
import random
import pickle
import sys
import re

from nltk.tokenize import word_tokenize
from tqdm import tqdm

import utils.utils as utils

RESERVED_WORDS = [
    "False", "class", "finally", "is", "return", "None", "continue", "for",
    "lambda", "try", "True", "def", "from", "nonlocal", "while", "and", "del",
    "global", "not", "with", "as", "elif", "if", "or", "yield", "assert",
    "else", "import", "pass", "break", "except", "in", "raise"
]

BUILTIN_FUNCTIONS = [
    "abs", "delattr", "hash", "memoryview", "set", "all", "dict", "help", "min",
    "setattr", "any", "dir", "hex", "next", "slice", "ascii", "divmod", "id",
    "object", "sorted", "bin", "enumerate", "input", "oct", "staticmethod",
    "bool", "eval", "int", "open", "str", "breakpoint", "exec", "isinstance",
    "ord", "sum", "bytearray", "filter", "issubclass", "pow", "super", "bytes",
    "float", "iter", "print", "tuple", "callable", "format", "len", "property",
    "type", "chr", "frozenset", "list", "range", "vars", "classmethod",
    "getattr", "locals", "repr", "zip", "compile", "globals", "map", "reversed",
    "__import__", "complex", "hasattr", "max", "round"
]

SYMBOLS = [
    "__", "++", "--", "**", "==", "~=", "||", "...", "<<", ">>", "<=", ">=", "->"
]


def clean_identifier(identifier):
    if "_" in identifier:
        snake_case_tokens = identifier.split("_")
    else:
        snake_case_tokens = [identifier]

    # If the identifier is an all uppercase acronym (like `WMA`) then we
    # need to capture that. But we also the case where the first two letters
    # are capitals but the first letter does not belong with the second
    # (like `AVariable`). We also need to capture the case of an acronym
    # followed by a capital for the next word (like `AWSVars`).
    camel_case_tokens = list()
    for token in snake_case_tokens:
        if not token.isupper():
            camel_split = re.split("([A-Z]+|[A-Z]?[a-z]+)(?=[A-Z]|\b)", token)
            camel_case_tokens.extend(camel_split)
        else:
            camel_case_tokens.append(token)

    char_digit_split = list()
    for token in camel_case_tokens:
        char_digit_split.extend(re.split("(\d+)", token))
    no_empty_tokens = [t for t in char_digit_split if t != ""]
    lower_case_toks = [t.lower() for t in no_empty_tokens]
    final_tokens = list()
    for token in lower_case_toks:
        if token.isdigit():
            new_toks = ["<BoINT>"] + [d for d in token] + ["<EoINT>"]
            final_tokens.extend(new_toks)
        else:
            final_tokens.append(token)
    return ["<BoN>"] + final_tokens + ["<EoN>"]


def clean_number(num_str):
    decimal_index = num_str.find(".")
    if decimal_index > -1:
        characteristic = num_str[:decimal_index]
        mantissa = num_str[decimal_index + 1:]

        characteristic_list = ["<BoINTP>"] + [d for d in characteristic] + ["<EoINTP>"]
        mantissa_list = ["<BoDECP>"] + [d for d in mantissa] + ["<EoDECP>"]
        return ["<BoFLT>"] + characteristic_list + ["."] + mantissa_list + ["<EoFLT>"]
    else:
        return ["<BoINT>"] + [d for d in num_str] + ["<EoINT>"]


def handle_alphas(alpha_str):
    has_unicode = not all([ord(c) < 128 for c in alpha_str])
    if has_unicode:
        print("Found unicode in alphas: ", alpha_str)

    if not alpha_str.isupper():
        camel_split = re.split("([A-Z]+|[A-Z]?[a-z]+)(?=[A-Z]|\b)", alpha_str)
        return [cstr.lower() for cstr in camel_split if cstr != ""]
    else:
        return [alpha_str.lower()]


def handle_digits(digit_str):
    has_unicode = not all([ord(c) < 128 for c in digit_str])
    if has_unicode:
        print("Found unicode in digits: ", digit_str)

    return ["<BoNUM>"] + [d for d in digit_str] + ["<EoNUM>"]


def handle_other(other):
    has_unicode = not all([ord(c) < 128 for c in other])
    if has_unicode:
        print("Found unicode in other: ", other)

    if "===" in other or "___" in other:
        return []

    other_list = re.split(r"(\*\*|\|\||--|\+\+|\.\.\.|~\=|__|\<\<|\>\>|\<\=|\>\=|-\>)", other)
    no_empties = [o for o in other_list if len(o) > 0]
    good_syms = list()
    for sym in no_empties:
        if sym in SYMBOLS:
            good_syms.append(sym)
        else:
            sym = sym.strip("'").strip("\\").strip("_")
            if len(sym) < 1:
                good_syms.append(sym)
    return good_syms


def strip_unicode(token):
    new_token = ""
    for c in token:
        if ord(c) < 128:                    # strips unicode
            new_token += c
    return new_token


def superclean_docstring(docstring):
    # STEPS: NOTE: skipping steps 1 and 2
    # 1. Check for math components
    # 2. Strip off any `__` tokens
    # 3. Separate out into {letters | digits | other}
        # NOTE: that digits should include `.`
        # NOTE: other should be sure to capture || as a symbol and | w/o any other context
    # 4. Split digits (be sure to do mantissa split if `.` is present)
    # 5a. Split letters on `.` and `_` with B/EoN tags and then split on camelCase
    # 5b. Normalize letters to lowercase
        # NOTE: do not make lowercase if |letters| == 1
    # 6. Strip unicode chars from any token (unless token is single unicode char)
    typed_tokens = list()
    for token in docstring:
        if len(token) == 0:
            continue

        if len(token) == 1:                         # No need to process char tokens
            if token.isdigit():
                typed_tokens.extend(handle_digits(token))
            else:
                typed_tokens.append(token)
            continue

        if all([not c.isalnum() for c in token]):   # handle pre-existing non alphanumeric strings
            no_unicode_token = strip_unicode(token)
            if len(no_unicode_token) > 0:
                typed_tokens.extend(handle_other(no_unicode_token))
            continue

        if token.isalpha():                         # handle only letters
            no_unicode_token = strip_unicode(token)
            if len(no_unicode_token) > 0:
                typed_tokens.extend(handle_alphas(no_unicode_token))
            continue

        if token.isdigit():                         # handle only digits
            typed_tokens.extend(handle_digits(token))
            continue

        cur_idx = 0
        cur_type = "none"
        cur_token = ""
        while cur_idx < len(token):
            if not ord(token[cur_idx]) < 128:       # strips unicode
                cur_idx += 1
                continue

            if token[cur_idx].isalpha():
                if cur_type == "alpha":
                    cur_token += token[cur_idx]
                else:
                    if len(cur_token) > 0:
                        if cur_type == "digit":
                            typed_tokens.extend(handle_digits(cur_token))
                        elif cur_type == "other":
                            typed_tokens.extend(handle_other(cur_token))
                    cur_type = "alpha"
                    cur_token = token[cur_idx]
            elif token[cur_idx].isdigit():
                if cur_type == "digit":
                    cur_token += token[cur_idx]
                else:
                    if len(cur_token) > 0:
                        if cur_type == "alpha":
                            typed_tokens.extend(handle_alphas(cur_token))
                        elif cur_type == "other":
                            typed_tokens.extend(handle_other(cur_token))
                    cur_type = "digit"
                    cur_token = token[cur_idx]
            else:
                if cur_type == "other":
                    cur_token += token[cur_idx]
                else:
                    if len(cur_token) > 0:
                        if cur_type == "alpha":
                            typed_tokens.extend(handle_alphas(cur_token))
                        elif cur_type == "digit":
                            typed_tokens.extend(handle_digits(cur_token))
                    cur_type = "other"
                    cur_token = token[cur_idx]
            cur_idx += 1

    return typed_tokens


class CodeCrawler():
    def __init__(self, corpus_name="code-comment-corpus", modules=[]):
        self.base_path = utils.CODE_CORPUS / "corpus"
        self.name = corpus_name
        self.mods = modules
        self.functions = dict()
        self.code_comment_pairs = dict()
        self.clean_code_data = dict()

    def build_function_dict(self):
        filepath = self.base_path / "code.pkl"
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

    def build_code_comment_pairs(self):
        if not self.functions:
            code_path = self.base_path / "code.pkl"
            if isfile(code_path):
                self.functions = pickle.load(open(code_path, "rb"))
            else:
                raise RuntimeWarning("Function dataset has not been built!!")

        filepath = self.base_path / "{}.pkl".format(self.name)
        code_filepath = self.base_path / "clean_code_data.pkl"
        if isfile(filepath) and isfile(code_filepath):
            self.code_comment_pairs = pickle.load(open(filepath, "rb"))
            self.clean_code_data = pickle.load(open(code_filepath, "rb"))
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
                        number_sequence = clean_number(token)
                        clean_code.extend(number_sequence)
                    elif tok_type == tok.STRING:
                        clean_code.append("<STRING>")
                    elif tok_type == tok.NAME:
                        if token in RESERVED_WORDS or token in BUILTIN_FUNCTIONS:
                            clean_code.append(token)
                        else:
                            identifier_sequence = clean_identifier(token)
                            clean_code.extend(identifier_sequence)
                    else:
                        clean_code.extend(token.split())

                self.clean_code_data[identifier] = clean_code
                if found_doc:
                    clean_doc = word_tokenize(clean_doc)
                    clean_doct_str = " ".join(clean_doc)
                    first_period = clean_doct_str.find(" . ")
                    if 0 < first_period < 5:
                        second_period = clean_doct_str.find(" . ", first_period + 3)
                        clean_doct_str = clean_doct_str[: second_period + 3]
                    elif first_period > 0:
                        clean_doct_str = clean_doct_str[: first_period + 3]

                    clean_doc = clean_doct_str.split()
                    clean_doc = superclean_docstring(clean_doc)

                    if len(clean_code) <= 3000 and len(clean_doc) <= 300:
                        clean_code = ["<BoC>"] + clean_code + ["<EoC>"]
                        clean_doc = ["<BoL>"] + clean_doc + ["<EoL>"]
                        self.code_comment_pairs[identifier] = (clean_code, clean_doc)
            except tok.TokenError as e:
                print(e)

        # sys.exit()

        code = [(name, code) for name, (code, comm) in self.code_comment_pairs.items()]
        print("Sorting code")
        code.sort(key=lambda tup: tup[1])
        print("Code is sorted")

        list_of_dup_lists = list()
        for idx, (name1, code1) in enumerate(tqdm(code, desc="Finding dups")):
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

        prev_length = len(self.code_comment_pairs.keys())
        for dup_list in list_of_dup_lists:
            for key in dup_list[1:]:
                if key in self.code_comment_pairs:
                    del self.code_comment_pairs[key]
        new_length = len(self.code_comment_pairs.keys())
        print("Code/comm had {} examples, now has {} examples".format(prev_length, new_length))

        code = [(name, code) for name, code in self.clean_code_data.items()]
        print("Sorting code")
        code.sort(key=lambda tup: tup[1])
        print("Code is sorted")

        list_of_dup_lists = list()
        for idx, (name1, code1) in enumerate(tqdm(code, desc="Finding dups")):
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

        prev_length = len(self.clean_code_data.keys())
        for dup_list in list_of_dup_lists:
            for key in dup_list[1:]:
                if key in self.clean_code_data:
                    del self.clean_code_data[key]
        new_length = len(self.clean_code_data.keys())
        print("Full code had {} examples, now has {} examples".format(prev_length, new_length))

        pickle.dump(self.code_comment_pairs, open(filepath, "wb"))
        pickle.dump(self.clean_code_data, open(code_filepath, "wb"))

    def get_sentence_output(self):
        if not self.code_comment_pairs:
            raise RuntimeWarning("Code/comment dataset has not been built!!")

        outcode = self.base_path / "code-sentences.txt"
        outcomm = self.base_path / "comm-sentences.txt"
        outcodefull = self.base_path / "code-sentences-full.txt"

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

    def output_clean_comments(self):
        clean_comments = dict()
        for key, (code, comm) in tqdm(self.code_comment_pairs.items(), desc="Cleaning comments"):
            comm_str = " ".join(comm)
            clean_comm = comm_str.replace("*", "STAR").replace("/", "DIV") \
                                 .replace("+", "PLUS").replace("-", "SUB") \
                                 .replace("?", "QUE").replace("\\", "SLSH") \
                                 .replace("`", "BTCK").replace("'", "TCK") \
                                 .replace("(", "LPAR").replace(")", "RPAR") \
                                 .replace("[", "LBKT").replace("]", "RBKT") \
                                 .replace("{", "LCRL").replace("}", "RCRL") \
                                 .replace("|", "BAR").replace("!", "BNG") \
                                 .replace(":", "CLN").replace(";", "SCLN") \
                                 .replace("\"", "QTE").replace("=", "EQ") \
                                 .replace("<", "LCAR").replace(">", "RCAR") \
                                 .replace("@", "ATS").replace("#", "PND") \
                                 .replace("$", "DLR").replace("%", "PRCT") \
                                 .replace("^", "CAR").replace("&", "AMP") \
                                 .replace("~", "TLD")
            clean_comments[key] = clean_comm.split()

        comm_path = self.base_path / "clean-comments.pkl"
        pickle.dump(clean_comments, open(comm_path, "wb"))

    def init_functions_from_file(self, filepath):
        self.functions = pickle.load(open(filepath), "rb")

    def init_code_comment_corpus_from_file(self, filepath):
        self.code_comment_pairs = pickle.load(open(filepath), "rb")

    # def split_code_comment_data(self, filepath, train_size=0.8, val_size=0.15):
    #     if not self.code_comment_pairs:
    #         raise RuntimeWarning("Code/comment dataset has not been built!!")
    #
    #     arr_data = list(self.code_comment_pairs.values())
    #     random.shuffle(arr_data)
    #     # total_length = len(arr_data)
    #     # train_length = int(train_size * total_length)
    #     # val_length = int(val_size * total_length) + train_length
    #
    #     (test_code, test_comm) = map(list, zip(*arr_data[:802]))
    #     (val_code, val_comm) = map(list, zip(*arr_data[802: 1802]))
    #     (train_code, train_comm) = map(list, zip(*arr_data[1802:]))
    #
    #     with open(join(filepath, "train.code"), "w") as outfile:
    #         for line in train_code:
    #             outfile.write("{}\n".format(" ".join(line)))
    #
    #     with open(join(filepath, "train.nl"), "w") as outfile:
    #         for line in train_comm:
    #             outfile.write("{}\n".format(" ".join(line)))
    #
    #     with open(join(filepath, "dev.code"), "w") as outfile:
    #         for line in val_code:
    #             outfile.write("{}\n".format(" ".join(line)))
    #
    #     with open(join(filepath, "dev.nl"), "w") as outfile:
    #         for line in val_comm:
    #             outfile.write("{}\n".format(" ".join(line)))
    #
    #     with open(join(filepath, "test.code"), "w") as outfile:
    #         for line in test_code:
    #             outfile.write("{}\n".format(" ".join(line)))
    #
    #     with open(join(filepath, "test.nl"), "w") as outfile:
    #         for line in test_comm:
    #             outfile.write("{}\n".format(" ".join(line)))
