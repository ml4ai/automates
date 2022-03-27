int main() {
    int x = 5;
    int y = 10;
    int i = 0;
    int divisible = 0;


    while (i < x) {
        ++i;

        if (y % i == 0) {
            divisible = 1;
        }

        y--;
    }

    return 0;

}

