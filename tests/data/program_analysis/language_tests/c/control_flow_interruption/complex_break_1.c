int main()
{
    int x = 10;
    int y = 0;
    while (y < x) 
    {
        y = y + 1;

        if (y == 5)
        {
            x = x - 1;
            break;
        }
        else
            y = 5;

        y = y - x;
    }

    return 1;
}