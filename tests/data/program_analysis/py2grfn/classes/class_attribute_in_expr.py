class Example:
    def __init__(self):
        self.x = 4

    def get_x(self):
        return self.x


def main():
    ex = Example()
    x = 12
    y = 10 + (x / ex.x)