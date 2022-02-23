double g1 = 0.0;

double func1(double x){
    g1 = x + 1;
    return x + 2;
}

int main(int argc, char **argv){
    double out0 = g1 * 2;
    double out1 = func1(2.0);
    double out2 = g1 * 3;

    return 0;
}

