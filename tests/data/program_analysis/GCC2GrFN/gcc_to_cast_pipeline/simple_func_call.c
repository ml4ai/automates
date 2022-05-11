int func(int x) {
    return -1;
}

int main() {
    int x = 3;
    int z = x + 2 * func(x) - 1;
}
