#include <stdio.h>

int sum(int a, int b, int c, int d, int e, int f, int g, int h){
    return a + b + c + d + e + f + g + h;
}

int main() {
    int a = 1;
    int b = 2;
    int c = 3;
    int d = 4;
    int e = 5;
    int f = 6;
    int g = 7;
    int h = 8;
    int res  = sum(a, b, c, d, e, f, g, h);
    printf("res: %d", res);
    return 0;
}
