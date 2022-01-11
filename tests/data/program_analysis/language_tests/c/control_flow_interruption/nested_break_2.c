int main()
{
    int x = 10;
    int y = 0;
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
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
    }
    return 1;
}