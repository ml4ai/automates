int main() {
    int a = 5;
    int b = 3;
    int x = 0;

    if (a > b) {
        x = b;
        b = a;
    }

    if (x == 3) {
        a = x;
        b = a;
        x = 10;
    }

    return 0;
}
