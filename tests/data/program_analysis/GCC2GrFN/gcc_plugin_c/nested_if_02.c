
int main() {
    int x = 5;
    int y = 3;

    int a = 2;
    int b = 4;

    if (y < x) {
        ++a;
        --b;

        if (a < b) {
            ++x;
            if ( a < 3 ) {
                ++y;
                if (a > 0) {
                    ++a;
                }
                else if (b > 3) {
                    --x;
                }
            }
            else {
                --y;
            }
            
        }

        --y;

        if (b < x) {
            ++y;
        }

        --b;
    }

    return 0;

}
