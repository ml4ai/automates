# Tests we have multiple decision nodes leaving the if container
# for each variable defined in the body.

def main():
    x = 1
    y = 2

    # y should have both conditions incoming, x/z should only
    # have the first condition, and z should have two potential
    # updates. Also, z should have a definition automatically 
    # created before the if container as it isnt implicitly 
    # defined
    if x == 1:
        y = x + x
        y = x + 1
        x = 3
        z = 2
    elif x == 2:
        y = x * x
    else:
        z = 3
