int main() {
    int a = 5;
    int b = 3;
    int x = 0;

    if (a < b) {
        x = b;
        b = a;
    }
    // else if should be taken
    else if (x < a) {
        x = a;
        b = 0;
    }
    // x is 5 
    // a is 5
    // b is 0

    // if should be taken
    if (x == 5) {
        b = 7;
        a = 10;
    }
    // else if is still true though
    else if (b < 10) {
        x = x + 1;
    }
    // x is 5
    // a is 10
    // b is 7

    return 0;
}
