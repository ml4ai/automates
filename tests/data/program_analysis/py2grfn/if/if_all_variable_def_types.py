# Represents all the types of variables being defined (or
# nor defined) and then used in an if body

# Given the inputs foo(1,2,3,4), should return 240
def foo(c1, c2, c3, c4):
    a = 1
    b = 2
    c = 3
    d = 4
    if c1:
        a = 5
        b = 4
        f = 0
    elif c2:
        b = 3
        c = 3
        f = 0
    elif c3:
        e = 5
        b = 0
        f = 0
    elif c4:
        a = 3
        b = 1
        f = 0
    else:
        b = 2
        f = 0
        b = 2*b
    x =  a * b * c * d
