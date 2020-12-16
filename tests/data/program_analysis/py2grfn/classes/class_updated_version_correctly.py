class Example:
    def __init__(self):
        self.x = 0
        self.y = 1

    def increment_x(self):
        self.x += 1
        return self.x

    def increment_y(self):
        self.y += 1
        return self.y


def main():
    ex = Example()
    ex.increment_x()
    ex.increment_y()
    ex.increment_x()
    ex.increment_y()

    x = ex.increment_x()
    y = ex.increment_y()