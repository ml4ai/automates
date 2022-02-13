// Declares and initializes variables that are then in fn call
#include <stdio.h>

int add2(int x0, int x1) {
    return x0 + x1;
}

int main() {
    int x0 = 8;
    int x1 = 9;
    int x2;
    x2 = add2(x0, x1);
    printf("Answer: %d\n", x2);
    return 0;
}