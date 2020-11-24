# Tests if/elif/else statement as elif/else are handled differently
# Ensure we handle the combination of both

def main():
    x = 1
    y = 0

    if x == 0:
        y = 1
    elif x == 1:
        y = 2
    else:
        y = 3

    return y