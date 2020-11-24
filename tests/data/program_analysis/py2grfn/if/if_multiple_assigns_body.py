# Tests only one edges goes to the decision per body even if there are 
# multiple assignments in one body

def main():
    x = 1
    y = 2

    # y should only have two inputs to the decision even though there 
    # are three assignments in the body
    if x == 1:
        y = x + x
        y = x + 1
    else:
        y = x * x
