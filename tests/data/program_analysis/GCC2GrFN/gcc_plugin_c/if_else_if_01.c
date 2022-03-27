int func(int input)
{
    int x = 0;
    if (input > 10) {
        x = 100;
    } else if (input >= 100) {
          x = 10;
    } else {
        x = 1;
    }
    return x;
}

int main()
{
    int y = func(1000);
    return y;
}