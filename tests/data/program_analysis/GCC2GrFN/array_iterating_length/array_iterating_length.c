int main()
{

    int arr[5] = {1, 2, 3, 4, 5};

    for (int i = 0; i < (sizeof arr / sizeof arr[0]); i++)
    {
        arr[i] = arr[i] * 2;
    }

    return 0;
}