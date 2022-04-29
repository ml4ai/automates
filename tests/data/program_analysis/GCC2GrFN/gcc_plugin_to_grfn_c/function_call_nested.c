int i(int y)
{
    y -= (y / 2);

    return y;
}

int h(int x)
{
    int temp = x / i(x);
    return temp;
}

int g(int y)
{
    return h(y) + y;
}

int f(int x)
{
    int res = x * g(x);
    return res;
}

int main()
{
    int arg = 12;
    int onesixtyeight = f(arg);

    return 0;
}