int multiply(int x, int y)
{
    int temp = x * y;
    return temp;
}

int main()
{
    int arg = 10;
    int arg2 = 20;

    // Expression arguments in both positions
    int r1 = multiply(5 * arg, (5 + 20 / arg) * arg2);

    // Expression args using just literals
    int r2 = multiply(5 * 5, 1 * (4 / 2));

    // Expression arg in just one position
    int r3 = multiply(arg, arg * 2 + 5);
    int r4 = multiply(5, arg * 2 + 5);

    return 0;
}