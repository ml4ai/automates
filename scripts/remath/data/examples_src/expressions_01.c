#include <stdio.h>
int main() {
    int x0 = 8;
    int x1 = 9;
    int x2;
    int x3;
    int x4;
    int x5;
    x2 = x0 + x1;
    x3 = 45 / (x1 * x2);
    x4 = x2 - x3;
    x5 = (x0 % 3) * x3 + (x0 + x3);
    printf("Answer: %d\n", x5);
    return 0;
}