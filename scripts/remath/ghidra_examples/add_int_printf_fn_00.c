// fn call inline in printf, with literals
#include <stdio.h>

int add2(int x0, int x1) {
    return x0 + x1;
}

int main() {
    printf("Answer: %d\n", add2(1, 2));
    return 0;
}