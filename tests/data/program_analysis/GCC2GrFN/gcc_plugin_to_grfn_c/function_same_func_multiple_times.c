int multiply(int x, int y)
{
    int temp = x * y;
    return temp;
}

int main()
{
    int five = 5;
    int ten = 10;
    int twenty = 20;

    int five_squared = multiply(five, five);
    int two_hundred = multiply(ten, twenty);
    int fifty = multiply(ten, five);

    return 0;
}