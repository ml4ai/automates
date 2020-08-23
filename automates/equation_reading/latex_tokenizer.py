from enum import IntEnum
from collections import namedtuple, defaultdict
from string import ascii_letters


Token = namedtuple("Token", "value code")


class CategoryCode(IntEnum):
    # Escape character; this signals the start of a control sequence.
    # IniTeX makes the backslash \ (code 92) an escape character.
    Escape = 0
    # Beginning of group; such a character causes TeX to enter a new level of
    # grouping. The plain format makes the open brace { a beginning-of-group
    # character.
    StartOfGroup = 1
    # End of group; TeX closes the current level of grouping.
    # Plain TeX has the closing brace } as end-of-group character.
    EndOfGroup = 2
    # Math shift; this is the opening and closing delimiter for math formulas.
    # Plain TeX uses the dollar sign $ for this.
    MathShift = 3
    # Alignment tab; the column (row) separator in tables made with
    # \halign (\valign).
    # In plain TeX this is the ampersand &.
    Alignment = 4
    # End of line; a character that TeX considers to signal the end of an
    # input line.
    # IniTeX assigns this code to the <return>, that is, code 13.
    EndOfLine = 5
    # Parameter character; this indicates parameters for macros.
    # In plain TeX this is the hash sign.
    Parameter = 6
    # Superscript; this precedes superscript expressions in math mode.
    # It is also used to denote character codes that cannot be entered in
    # an input file.
    # In plain TeX this is the circumflex ^.
    Superscript = 7
    # Subscript; this precedes subscript expressions in math mode.
    # In plain TeX the underscore _ is used for this.
    Subscript = 8
    # Ignored; characters of this category are removed from the input,
    # and have therefore no influence on further TeX processing.
    # In plain TeX this is the <null> character, that is, code 0.
    Ignored = 9
    # Space; space characters receive special treatment.
    # IniTeX assigns this category to the ASCII <space> character, code 32.
    Space = 10
    # Letter; in IniTeX only the characters a..z, A..Z are in this category.
    # Often, macro packages make some ‘secret’ character (for instance @)
    # into a letter.
    Letter = 11
    # Other; IniTeX puts everything that is not in the other categories into
    # this category. Thus it includes, for instance, digits and punctuation.
    Other = 12
    # Active; active characters function as a TeX command, without being
    # preceded by an escape character.
    # In plain TeX this is only the tie character ~ , which is defined to
    # produce an unbreakable space
    Active = 13
    # Comment character; from a comment character onwards, TeX considers the
    # rest of an input line to be comment and ignores it.
    # In IniTeX the percent sign % is made a comment character.
    Comment = 14
    # Invalid character; this category is for characters that should not appear
    # in the input.
    # IniTeX assigns the ASCII <delete> character, code 127, to this category.
    Invalid = 15


class LatexTokenizer:
    # TeX's input processor can be considered to be a finite state automaton
    # with three internal states, that is, at any moment in time it is in one
    # of three states, and after transition to another state there is no memory
    # of the previous states.

    # State N is entered at the beginning of each new input line, and that is
    # the only time TeX is in this state. In state N all space tokens (that is,
    # characters of category 10) are ignored; an end-of-line character is
    # converted into a \par token. All other tokens bring TeX into state M.

    # State S is entered in any mode after a control word or control space
    # (but after no other control symbol), or, when in state M, after a space.
    # In this state all subsequent spaces or end-of-line characters in this
    # input line are discarded.

    # By far the most common state is M, 'middle of line'.
    # It is entered after characters of categories 1–4, 6–8, and 11–13, and
    # after control symbols other than control space. An end-of-line character
    # encountered in this state results in a space token.

    def __init__(self, text=None):
        # caracters not registered in the category_codes look-up table get a
        # code 12 (Other)
        self.category_codes = defaultdict(lambda: CategoryCode.Other)
        # register defaults
        self.category_codes.update(
            {
                "\\": CategoryCode.Escape,
                "{": CategoryCode.StartOfGroup,
                "}": CategoryCode.EndOfGroup,
                "$": CategoryCode.MathShift,
                "&": CategoryCode.Alignment,
                "\n": CategoryCode.EndOfLine,
                "#": CategoryCode.Parameter,
                "^": CategoryCode.Superscript,
                "_": CategoryCode.Subscript,
                "\0": CategoryCode.Ignored,
                " ": CategoryCode.Space,
                "\t": CategoryCode.Space,
                "~": CategoryCode.Active,
                "%": CategoryCode.Comment,
                "\x7f": CategoryCode.Invalid,
            }
        )
        # register ascii letters
        for c in ascii_letters:
            self.category_codes[c] = CategoryCode.Letter
        # reset tokenizer
        self.reset(text)

    def __iter__(self):
        while self.has_token():
            yield self.get_token()

    def reset(self, text=None):
        """Resets the tokenizer with optional new input text."""
        if text is not None:
            self.text = text
            self.chars = list(text)
        self.state = "N"
        self.idx = 0

    def register_category_code(self, char, code):
        """Register a category code for a given character."""
        self.category_codes[char] = code

    def unregister_category_code(self, char):
        """Removes character from category_codes table."""
        if char in self.category_codes:
            del self.category_codes[char]

    def has_token(self):
        """Returns True if there is at least one more token."""
        return self.idx < len(self.chars)

    def get_token(self):
        """Returns (token, code) tuple, or None if there are no more tokens."""
        while self.has_token():
            token = self.chars[self.idx]
            code = self.category_codes[token]
            self.idx += 1
            if code == CategoryCode.Escape and self.has_token():
                next_char = self.chars[self.idx]
                next_code = self.category_codes[next_char]
                self.idx += 1
                if next_code == CategoryCode.Letter:
                    # An escape character -- that is, a character of category
                    # 0 -- followed by a string of ‘letters’ is lumped together
                    # into a control word, which is a single token.
                    self.state = "S"
                    token += next_char
                    while self.has_token():
                        next_char = self.chars[self.idx]
                        next_code = self.category_codes[next_char]
                        if next_code == CategoryCode.Letter:
                            token += next_char
                            self.idx += 1
                        else:
                            break
                elif next_code == CategoryCode.Space:
                    # The control symbol that results from an escape character
                    # followed by a space character is called control space.
                    self.state = "S"
                    token += next_char
                else:
                    # Escape character followed by a single character that is
                    # not of category 11, letter, is made into a control symbol
                    self.state = "M"
                    token += next_char
                code = None
            if code == CategoryCode.EndOfLine:
                # handle a new line according to the current state
                if self.state == "M":
                    self.state = "N"
                    token = " "
                    code = CategoryCode.Space
                elif self.state == "N":
                    token = "\\par"
                    code = None
                elif self.state == "S":
                    self.state = "N"
                    continue
            elif (
                code == CategoryCode.Parameter
                and self.chars[self.idx].isdigit()
            ):
                # Parameter tokens: a parameter character -- that is, a
                # character of category 6, by default -- followed by a
                # digit 1..9 is replaced by a parameter token.
                token += self.chars[self.idx]
                self.idx += 1
                self.state = "M"
                code = None
            elif code == CategoryCode.Space:
                # handle spaces according to the current state
                if self.state in ("N", "S"):
                    continue
                else:
                    self.state = "S"
            elif code == CategoryCode.Comment:
                # discard tokens until the end of line
                while self.has_token():
                    next_char = self.chars[self.idx]
                    next_code = self.category_codes[next_char]
                    self.idx += 1
                    if next_code == CategoryCode.EndOfLine:
                        self.state = "N"
                        break
                continue
            elif code in (
                CategoryCode.StartOfGroup,
                CategoryCode.EndOfGroup,
                CategoryCode.MathShift,
                CategoryCode.Alignment,
                CategoryCode.Parameter,
                CategoryCode.Superscript,
                CategoryCode.Subscript,
                CategoryCode.Letter,
                CategoryCode.Other,
                CategoryCode.Active,
            ):
                self.state = "M"
            return Token(token, code)
