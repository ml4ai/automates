// Argument literals directly in fn call
#include <stdio.h>

int add2(int x0, int x1) {
    return x0 + x1;
}

int main() {
    int x2;
    x2 = add2(1, 2);
    printf("Answer: %d\n", x2);
    return 0;
}