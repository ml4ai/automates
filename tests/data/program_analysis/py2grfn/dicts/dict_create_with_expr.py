def main():
    a = 1
    b = 2
    c = 3

    # Our code should seperate the expressions out before this dict creation
    d = {"x": a + b, "y": (b, c), "z": [a + b, c + 3]}

    return d