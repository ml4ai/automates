#include <stdio.h>

int main() {
    int x = 0;
    int y = 5;
    if (x < y) {
        printf("x is less than y\n");
        if (y == 5) {
            x = y;
        }
    }

    return 0;
}
