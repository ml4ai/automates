int func(int x) {
    int y = 2 * x;

    return y;
}

int main() {
    int x = 3;
    int z = x + 2 * func(x) - 1;
    int w = z + 2 * func(x);
    int u = x + func(w + z*x);
}
