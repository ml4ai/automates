def json2js(json_data, output_file, var_name='eqn_src'):
    """
    Helper function to write 'json' version of latex source data as a javascript list of dicts.
    Use json.load() to read the json into python object.
    Args:
        json_data: Assumed format: [ {"src": <string>, "mml": <string>}, ... ]
        output_file: Path to .js output file
        var_name: Name of the variable being assigned the list of dicts in the .js file

    Returns:

    """
    with open(output_file, 'w') as fout:
        fout.write(f'{var_name} = [\n')
        for i, datum in enumerate(json_data):
            fout.write('  {\n')
            fout.write(f'    src: {repr(datum["src"])},\n')
            fout.write(f'    mml: {repr(datum["mml"])}\n')
            fout.write('  }')
            if i < len(json_data):
                fout.write(',')
            fout.write('\n')
        fout.write('];')


# Test
'''
data = [
  { "src": "P(E) = {n \\choose k} p^k (1-p)^{ n-k}",
    "mml": "<math xmlns=\"http://www.w3.org/1998/Math/MathML\" display=\"block\"> <mi>P</mi> <mo stretchy=\"false\">(</mo> <mi>E</mi> <mo stretchy=\"false\">)</mo> <mo>=</mo> <mrow> <mrow data-mjx-texclass=\"ORD\"> <mrow data-mjx-texclass=\"OPEN\"> <mo minsize=\"2.047em\" maxsize=\"2.047em\">(</mo> </mrow> <mfrac linethickness=\"0\"> <mi>n</mi> <mi>k</mi> </mfrac> <mrow data-mjx-texclass=\"CLOSE\"> <mo minsize=\"2.047em\" maxsize=\"2.047em\">)</mo> </mrow> </mrow> </mrow> <msup> <mi>p</mi> <mi>k</mi> </msup> <mo stretchy=\"false\">(</mo> <mn>1</mn> <mo>&#x2212;</mo> <mi>p</mi> <msup> <mo stretchy=\"false\">)</mo> <mrow> <mi>n</mi> <mo>&#x2212;</mo> <mi>k</mi> </mrow> </msup> </math>"
  },
  { "src": "\\begin{align} \\dot{x} \\& = \\sigma(y-x) \\\\ \\dot{y} \\& = \\rho x - y - xz \\\\ \\dot{z} \\& = -\\beta z + xy \\end{align}",
    "mml": "<math xmlns=\"http://www.w3.org/1998/Math/MathML\" display=\"block\"> <mtable displaystyle=\"true\" columnalign=\"right left right left right left right left right left right left\" columnspacing=\"0em 2em 0em 2em 0em 2em 0em 2em 0em 2em 0em\" rowspacing=\"3pt\"> <mtr> <mtd> <mrow> <mover> <mi>x</mi> <mo>&#x2D9;</mo> </mover> </mrow> </mtd> <mtd> <mi></mi> <mo>=</mo> <mi>&#x3C3;</mi> <mo stretchy=\"false\">(</mo> <mi>y</mi> <mo>&#x2212;</mo> <mi>x</mi> <mo stretchy=\"false\">)</mo> </mtd> </mtr> <mtr> <mtd> <mrow> <mover> <mi>y</mi> <mo>&#x2D9;</mo> </mover> </mrow> </mtd> <mtd> <mi></mi> <mo>=</mo> <mi>&#x3C1;</mi> <mi>x</mi> <mo>&#x2212;</mo> <mi>y</mi> <mo>&#x2212;</mo> <mi>x</mi> <mi>z</mi> </mtd> </mtr> <mtr> <mtd> <mrow> <mover> <mi>z</mi> <mo>&#x2D9;</mo> </mover> </mrow> </mtd> <mtd> <mi></mi> <mo>=</mo> <mo>&#x2212;</mo> <mi>&#x3B2;</mi> <mi>z</mi> <mo>+</mo> <mi>x</mi> <mi>y</mi> </mtd> </mtr> </mtable> </math>"
  },
  { "src": "\\left( \\sum_{k=1}^n a_k b_k \\right)^{\\!\\!2} \\leq \\left( \\sum_{k=1}^n a_k^2 \\right) \\left( \\sum_{k=1}^n b_k^2 \\right)",
    "mml": "<math xmlns=\"http://www.w3.org/1998/Math/MathML\" display=\"block\"> <msup> <mrow data-mjx-texclass=\"INNER\"> <mo data-mjx-texclass=\"OPEN\">(</mo> <munderover> <mo data-mjx-texclass=\"OP\">&#x2211;</mo> <mrow> <mi>k</mi> <mo>=</mo> <mn>1</mn> </mrow> <mi>n</mi> </munderover> <msub> <mi>a</mi> <mi>k</mi> </msub> <msub> <mi>b</mi> <mi>k</mi> </msub> <mo data-mjx-texclass=\"CLOSE\">)</mo> </mrow> <mrow> <mstyle scriptlevel=\"0\"> <mspace width=\"negativethinmathspace\"></mspace> </mstyle> <mstyle scriptlevel=\"0\"> <mspace width=\"negativethinmathspace\"></mspace> </mstyle> <mn>2</mn> </mrow> </msup> <mo>&#x2264;</mo> <mrow data-mjx-texclass=\"INNER\"> <mo data-mjx-texclass=\"OPEN\">(</mo> <munderover> <mo data-mjx-texclass=\"OP\">&#x2211;</mo> <mrow> <mi>k</mi> <mo>=</mo> <mn>1</mn> </mrow> <mi>n</mi> </munderover> <msubsup> <mi>a</mi> <mi>k</mi> <mn>2</mn> </msubsup> <mo data-mjx-texclass=\"CLOSE\">)</mo> </mrow> <mrow data-mjx-texclass=\"INNER\"> <mo data-mjx-texclass=\"OPEN\">(</mo> <munderover> <mo data-mjx-texclass=\"OP\">&#x2211;</mo> <mrow> <mi>k</mi> <mo>=</mo> <mn>1</mn> </mrow> <mi>n</mi> </munderover> <msubsup> <mi>b</mi> <mi>k</mi> <mn>2</mn> </msubsup> <mo data-mjx-texclass=\"CLOSE\">)</mo> </mrow> </math>"
  },
  { "src": "\\mathbf{V}_1 \\times \\mathbf{V}_2 = \\begin{vmatrix} \\mathbf{i} \\& \\mathbf{j} \\& \\mathbf{k} \\\\ \\frac{\\partial X}{\\partial u} \\& \\frac{\\partial Y}{\\partial u} \\& 0 \\\\ \\frac{\\partial X}{\\partial v} \\& \\frac{\\partial Y}{\\partial v} \\& 0 \\\\ \\end{vmatrix}",
    "mml": "<math xmlns=\"http://www.w3.org/1998/Math/MathML\" display=\"block\"> <msub> <mrow> <mi mathvariant=\"bold\">V</mi> </mrow> <mn>1</mn> </msub> <mo>&#xD7;</mo> <msub> <mrow> <mi mathvariant=\"bold\">V</mi> </mrow> <mn>2</mn> </msub> <mo>=</mo> <mrow data-mjx-texclass=\"INNER\"> <mo data-mjx-texclass=\"OPEN\">|</mo> <mtable columnspacing=\"1em\" rowspacing=\"4pt\"> <mtr> <mtd> <mrow> <mi mathvariant=\"bold\">i</mi> </mrow> </mtd> <mtd> <mrow> <mi mathvariant=\"bold\">j</mi> </mrow> </mtd> <mtd> <mrow> <mi mathvariant=\"bold\">k</mi> </mrow> </mtd> </mtr> <mtr> <mtd> <mfrac> <mrow> <mi mathvariant=\"normal\">&#x2202;</mi> <mi>X</mi> </mrow> <mrow> <mi mathvariant=\"normal\">&#x2202;</mi> <mi>u</mi> </mrow> </mfrac> </mtd> <mtd> <mfrac> <mrow> <mi mathvariant=\"normal\">&#x2202;</mi> <mi>Y</mi> </mrow> <mrow> <mi mathvariant=\"normal\">&#x2202;</mi> <mi>u</mi> </mrow> </mfrac> </mtd> <mtd> <mn>0</mn> </mtd> </mtr> <mtr> <mtd> <mfrac> <mrow> <mi mathvariant=\"normal\">&#x2202;</mi> <mi>X</mi> </mrow> <mrow> <mi mathvariant=\"normal\">&#x2202;</mi> <mi>v</mi> </mrow> </mfrac> </mtd> <mtd> <mfrac> <mrow> <mi mathvariant=\"normal\">&#x2202;</mi> <mi>Y</mi> </mrow> <mrow> <mi mathvariant=\"normal\">&#x2202;</mi> <mi>v</mi> </mrow> </mfrac> </mtd> <mtd> <mn>0</mn> </mtd> </mtr> </mtable> <mo data-mjx-texclass=\"CLOSE\">|</mo> </mrow> </math>"
  }
]


json2js(data, 'example_data.js')

'''
