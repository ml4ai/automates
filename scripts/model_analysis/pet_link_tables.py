import json
import sys

import model_analysis.linking as linking


grfn = json.load(open(sys.argv[1], "r"))
tables = linking.make_link_tables(grfn)
linking.print_table_data(tables)
