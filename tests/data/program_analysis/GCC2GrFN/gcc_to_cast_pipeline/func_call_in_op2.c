int func(int x) {
    int y = 2 * x;

    return y;
}

int main() {
    int x = 3;
    int z = x + 2 * func(3) - 1;
}
