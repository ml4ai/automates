def foo(x):
    return x + 3
x = foo(2)


# two ways to fix this
# 1. Follow the GrFN approach and make a 'placeholder' function def for foo
    # then fill out the contents of this placeholder once we actually reach the definition of foo

# 2. Restore the actual CAST order probably at the python to CAST level
    # in other words after visiting everything, determine how to make the CAST match the actual program source code
