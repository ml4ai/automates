int func1(int x){
    for(int i = 0; i < 5; i++)
    {
        for(int j = 0; j < 5; j++)
        {
            if(((i + j + x) % 2) == 1)
            {
                return -1;
            }
        }
    }
    return 0;
}

int main()
{
    int x = func1(10);
}