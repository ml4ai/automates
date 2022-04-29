int main() {
    int x = 5;
    int y = 10;
    int i = 0;
    int divisible = 0;


while_loop: while (i < x) {
        ++i;

        for (int z = 0; z < 5; ++z) {
            if (i % z == 0) {
                goto while_loop;
            }
        }

        if (y % i == 0) {
            divisible = 1;
        }

        y--;
    }

    return 0;

}

