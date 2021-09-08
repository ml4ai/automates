int multiply(int x, int y)
{
    int temp = x * y;
    return temp;
}

int main()
{
    int arg = 10;

    int five_squared = multiply(5, 5);
    int two_hundred = multiply(arg, 20);
    int fifty = multiply(5, arg);

    return 0;
}