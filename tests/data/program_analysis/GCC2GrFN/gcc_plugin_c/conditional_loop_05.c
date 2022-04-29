int main() {
    int x = 5;
    int y = 10;
    int i = 0;
    int divisible = 0;


    while (i < x) {
        ++i;

        for (int z = 0; z < 5; ++z) {
            if (i % z == 0) {
                continue;
            }
        }

        --y;
    }

    return 0;

}

