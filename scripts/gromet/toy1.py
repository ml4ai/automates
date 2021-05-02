def add1(x: float):
    return x + 1  # add1_exp


def toy1(x: float, y: int):
    z = x * y     # set_z_exp
    x = add1(z)   # reset_x_exp
    return x, z
