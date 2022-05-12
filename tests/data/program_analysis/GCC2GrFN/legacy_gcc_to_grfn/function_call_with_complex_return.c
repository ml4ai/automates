int func(int x)
{
    int squared = x * x;
    int cubed = squared * x;

    return (cubed / squared) * x;
}

int main()
{
    int arg = 3;
    int nine = func(arg);

    return 0;
}