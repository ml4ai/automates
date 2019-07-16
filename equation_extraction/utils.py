import subprocess
import os
from collect_data import render_tex, get_pages


def run_command(cmd, dirname, log_fn):
    with open(log_fn, 'w') as logfile:
        p = subprocess.Popen(cmd, stdout=logfile, stderr=subprocess.STDOUT, cwd=dirname)
        p.communicate()
        return_code = p.wait()
        return return_code

def load_segments(filename):
    with open(filename) as infile:
        lines = infile.readlines()
        lines = [line.strip() for line in lines]
        return lines

def render_equation(template_args, template, filename, keep_intermediate):
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    equation_tex = template.render(**template_args)
    with open(filename, 'w') as f:
        f.write(equation_tex)
    pdf_name = render_tex(filename, dirname, keep_intermediate)
    if pdf_name:
        image = get_pages(pdf_name, dump_pages=False, outdir="")[0]
    else:
        image = None
    return image