import subprocess


def run_command(cmd, dirname, log_fn):
    with open(log_fn, 'w') as logfile:
        p = subprocess.Popen(cmd, stdout=logfile, stderr=subprocess.STDOUT, cwd=dirname)
        p.communicate()
        return_code = p.wait()
        return return_code