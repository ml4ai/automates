from delphi.translators.for2py.format import *
from delphi.translators.for2py.arrays import *


def main():
    X = Array([(1,10)])
    arr = Array([(1,10)])

    X_constr = [11,22,33,44,55,66,77,88,99,110]
    X_subs = array_subscripts(X)
    X.set_elems(X_subs, X_constr)

    sub_arr = implied_loop_expr((lambda x:X.get_(x)), 3,8,1)
    arr_constr = flatten([10,20,sub_arr, 90, 100])
    arr_subs = array_subscripts(arr)

    arr.set_elems(arr_subs, arr_constr)

    fmt_obj = Format(['I5'])

    for i in range(1,10+1):
        val = arr.get_((i,))
        sys.stdout.write(fmt_obj.write_line([val]))

main()
