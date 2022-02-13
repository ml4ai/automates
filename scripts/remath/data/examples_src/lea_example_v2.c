#include <stdio.h>
int main() {
    long x5 = 5;
    int x4 = 4;
    long long x3 = 3;
    int x2 = (-26 % (-100 + (31 % (x4 / -16))));
    long long x1 = (x3 & (x5 | (29 ^ x5)));
    long long x0 = (x2 & x1);
    printf("Answer: %lld\n", x0);
    return 0;
    // return x0;
}