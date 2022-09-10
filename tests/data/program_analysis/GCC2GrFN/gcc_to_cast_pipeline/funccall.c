int func(int x, int y) {
    y = y + 2 * x;
    return y;
}

int main() {
    int x = 3;
    int z = func(x, 3) - 1;
}
