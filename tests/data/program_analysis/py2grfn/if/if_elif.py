# Tests if/elif statement as it is handled differently then elif

def main():
    x = 1
    y = 0

    if x == 0:
        y = 1
    elif x == 1:
        y = 2

    return y