int main() {
    int a = 5;
    int b = 3;
    int x = 0;

    if (a < b) {
        x = b;
        b = a;
    }
    // else should be taken
    else {
        x = a;
        a = b;
    }
    // x is 5 
    // a is 3
    // b is 3

    // if should be taken
    if (x == 5) {
        b = x;
        a = 10;
    }
    else {
        x = x + 1;
    }
    // x is 5
    // a is 10
    // b is 5

    return 0;
}
