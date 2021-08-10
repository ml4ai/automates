int main()
{

    int arr[27] = {2};
    int index = 0;
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            for (int k = 0; k < 3; k++)
            {
                arr[index] *= 2;
                index += 1;
            }
        }
    }

    int x = arr[26];
}