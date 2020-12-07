# Tests we handle if statements nested within eachother 

def main():
    x = 1
    y = 0
    z = 4

    if x == 0:
        y = 2
        # z = 2
        if y > 2:
            y = 2
            if z == 4:
                y = 3
        else:
            y = 1
    elif x == 1:
        if y > 2:
            y = 2
            if z == 4:
                y = 3
            else:
                y  = 1
    
    return y