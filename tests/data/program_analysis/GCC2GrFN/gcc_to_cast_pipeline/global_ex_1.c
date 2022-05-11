double g1 = 0.0;

double func1(double x){
    double y = g1 + 2;
    x = x + 10;
    g1 = x + 1;
    y = x + 4;
    return y + 2;
}

int main(int argc, char **argv){
    g1 = g1 + 1.0;
    double out1 = func1(2.0);
    out1 = func1(5.0);
    double out2 = g1 * 3;

    return 0;
}

