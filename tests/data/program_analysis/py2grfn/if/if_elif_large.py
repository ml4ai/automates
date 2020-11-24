# Tests we handle many elif statements

def main():
    x = 1
    y = 0

    if x == 0:
        y = 1
    elif x == 1:
        y = 2
    elif x == 2:
        y = 3
    elif x == 3:
        y = 4
    elif x == 4:
        y = 5

    return y