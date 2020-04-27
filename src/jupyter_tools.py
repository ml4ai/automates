import os
from IPython.display import HTML, Code, Image
import pygments
import subprocess as sp


def display_code(file: str):
    try:
        lexer = pygments.lexers.get_lexer_for_filename(file)
    except:
        from pygments.lexers.fortran import FortranLexer

        lexer = FortranLexer()

    with open(file, "r") as f:
        code = f.read()

    formatter = pygments.formatters.HtmlFormatter(
        linenos="inline", cssclass="pygments"
    )
    html_code = pygments.highlight(code, lexer, formatter)
    css = formatter.get_style_defs(".pygments")
    html = f"<style>{css}</style>{html_code}"

    return HTML(html)


def display_image(file: str):
    return Image(file, retina=True)


def get_python_shell():
    """Determine python shell

    get_python_shell() returns

    'shell' (started python on command line using "python")
    'ipython' (started ipython on command line using "ipython")
    'ipython-notebook' (e.g., running in Spyder or started with "ipython qtconsole")
    'jupyter-notebook' (running in a Jupyter notebook)

    See also https://stackoverflow.com/a/37661854
    """

    env = os.environ
    shell = "shell"
    program = os.path.basename(env["_"])

    if "jupyter-notebook" in program:
        shell = "jupyter-notebook"
    elif "JPY_PARENT_PID" in env or "ipython" in program:
        shell = "ipython"
        if "JPY_PARENT_PID" in env:
            shell = "ipython-notebook"

    return shell


def print_commit_hash_message():
    commit_hash = sp.check_output(["git", "rev-parse", "HEAD"])
    print(
        f"This notebook has been rendered with commit {commit_hash[:-1]} of"
        " Delphi."
    )


def display(A):
    from IPython.core.display import Image

    temporary_image_filename = "tmp.png"
    try:
        A.draw(temporary_image_filename, prog="dot")
        return Image(temporary_image_filename)
    finally:
        os.remove(temporary_image_filename)
