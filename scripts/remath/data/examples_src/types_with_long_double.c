#include <stdio.h>
int main() {
    int x0 = 7;
    long x1 = 98;
    long long x2 = 283;
    float x3 = 7.23;
    double x4 = -88.3;
    long double x5 = 123.92;
    long double x6 = x0 + x1 + x2 + x3 + x4 + x5;
    printf("Answer: %Lg\n", x6);
    return 0;
}