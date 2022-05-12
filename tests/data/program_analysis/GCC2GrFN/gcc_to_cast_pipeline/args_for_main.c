
double func1(double x){
    double y = x + 2.0;
    return y + 2;
}

int main(int argc, char **argv){
    double out1 = func1(2.0);
    out1 = func1(5.0);

    return 0;
}

