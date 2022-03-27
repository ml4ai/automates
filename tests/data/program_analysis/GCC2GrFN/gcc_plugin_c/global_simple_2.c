double g1;

double func1(double x){
    g1 = x + 1;
    return x + 2;
}

int main(int argc, char **argv){
    g1 = 1;
    g1 = g1 + 1.0;
    double out1 = func1(2.0);
    double out2 = g1 * 3;

    return 0;
}

