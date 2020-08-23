import pytest

from automates.equation_reading.decoding import tex2py


def test_tex2py():
    latex_input_file = "tests/data/equation_reading/sample_equations.txt"
    sympy_output_file = "tests/data/equation_reading/sample_output.txt"

    tex_eqns, sympy_eqns = list(), list()
    with open(latex_input_file, "r") as tex_infile:
        for tex_eqn_line in tex_infile:
            tex_eqns.append(tex_eqn_line.strip())

    with open(sympy_output_file, "r") as sympy_outfile:
        for sympy_line in sympy_outfile:
            sympy_eqns.append(sympy_line.strip())

    in_out_pairs = list(zip(tex_eqns, sympy_eqns))
    for tex_input, sympy_output in in_out_pairs:
        (_, obs_sympy_output) = tex2py(tex_input, include_sanitized=True)
        assert str(obs_sympy_output) == sympy_output
