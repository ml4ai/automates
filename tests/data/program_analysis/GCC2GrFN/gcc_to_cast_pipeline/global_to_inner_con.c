int g = 0;

int main() {
    int x = 0;

    while (x < 3) {
        ++x;
        if (x == 2) {
            int y = g + 1;
        }
    }

    return 0;
}
