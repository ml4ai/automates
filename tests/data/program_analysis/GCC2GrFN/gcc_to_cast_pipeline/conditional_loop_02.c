int main() {
    int x = 5;
    int y = 10;
    int i = 0;
    int divisible = 0;


    if (y / x == 2) {

        y += x;
        for (i = 0; i < 3; ++i) {
            x -= i;
        }

        divisible = 1;
    }

}

