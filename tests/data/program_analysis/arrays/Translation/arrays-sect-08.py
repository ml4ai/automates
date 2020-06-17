from delphi.translators.for2py.format import *
from delphi.translators.for2py.arrays import *

def main():
    A = Array([(1,5)])
    B = Array([(1,3)])

    # B = (/1,3,5/)
    B.set_elems(array_subscripts(B), [1,3,5])

    for i in range(1,5+1):
        A.set_(i, 0)

    fmt_obj = Format(['5(I5)'])

    sys.stdout.write(fmt_obj.write_line([A.get_(1), A.get_(2), A.get_(3), A.get_(4), A.get_(5)]))

    A.set_elems(array_values(B), 17)

    sys.stdout.write(fmt_obj.write_line([A.get_(1), A.get_(2), A.get_(3), A.get_(4), A.get_(5)]))


main()
