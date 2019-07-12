import utils.utils as utils


max_line_length = 0
with open(utils.CODE_CORPUS / "corpus" / "code-sentences.txt", "r") as codefile:
    for line in codefile:
        words = line.strip().split(" ")
        line_length = len(words)
        if line_length > max_line_length:
            max_line_length = line_length
print(f"Maximum line length is: {max_line_length}")
