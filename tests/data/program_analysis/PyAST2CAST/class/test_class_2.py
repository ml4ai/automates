class Foo():
    def __init__(self):
        self.x = 1
        self.y = 2

    def bar(self):
        self.x = self.y
        return self.x

def main():
    f = Foo()
    f.bar()

main()