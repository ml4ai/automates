# Tests if/else statement as it is handled differently then elif

def main():
    x = 1
    y = 0

    if x == 0:
        y = 1
    else:
        y = 2

    return y