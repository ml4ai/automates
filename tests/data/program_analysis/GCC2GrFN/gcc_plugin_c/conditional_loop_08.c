int main() {
    int x = 5;
    int y = 10;
    int i = 0;
    int divisible = 0;


    while (i < x) {
        ++i;

        int z = 0;
        do {
            ++z;
            if (i % z == 0) {
                y = 3;
            }
        } while (z < 5);

        --y;
    }

    return 0;

}

