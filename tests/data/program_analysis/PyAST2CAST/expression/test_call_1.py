# Use a function call in an expression
def foo(x):
    return x * x

def main():
    x = 2
    y = 3 + foo(2)
    print(y)