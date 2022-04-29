double g1 = 0.0;

double func1(double x){
    g1 = x + 1;
    double y = g1 + 2;
    return x + 2;
}

int main(int argc, char **argv){
    g1 = g1 + 1.0;
    double out1 = func1(2.0);
    double out2 = g1 * 3;

    return 0;
}

