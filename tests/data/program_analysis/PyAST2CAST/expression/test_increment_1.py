class Foo():
    def __init__(self):
        self.x = 1

def main():
    i = 0
    i += 1
    i = i + 1

    f = Foo()
    f.x += 1 
    f.x = f.x + 1
main()