def main():

    d = {"x": 1, "y": (1, 2), "z": [1, 2, 3]}

    d["z"] = 2

    x = 1
    d["x"] = x + x

    return d