class Rectangle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def area(self):
        return self.get_x() * self.get_y()

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def add_to_x(self, t):
        return self.x + t


def main():
    two = 2
    five = 5
    r = Rectangle(two, five)
    r.get_x()
    r.add_to_x(two)
    y = r.x
    r.area()