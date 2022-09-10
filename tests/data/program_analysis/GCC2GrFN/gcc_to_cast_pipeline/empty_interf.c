#include <stdio.h>
int func(int x) {
    int y = 2 * x;
    return y;
}
int main() {
    int x = 3;
    if  (func(x)){
       printf("hey");
    }
}

