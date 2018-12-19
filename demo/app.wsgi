activate_this = '/home/ubuntu/automates/demo/venv/bin/activate_this.py'
with open(activate_this) as f:
        exec(f.read(), dict(__file__=activate_this))

import os
import sys
import logging

os.environ["DELPHI_DATA"] = "/home/ubuntu/automates_demo/data"
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/html/automates_demo/")

from app import app as application
