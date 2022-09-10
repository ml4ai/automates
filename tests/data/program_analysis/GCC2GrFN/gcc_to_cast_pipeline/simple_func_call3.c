int func(int x, int y) {
    return -1;
}

int main() {
    int x = 3;
    int z = x + 2 * func(x, x) - 1;
}
