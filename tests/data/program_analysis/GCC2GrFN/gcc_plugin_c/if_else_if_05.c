// Extra if-elseif-else statement in the body of the else-if
int func(int input)
{
    int x = 0;
    if (input > 10) {
        x = 100;
    } else if (input >= 100) {
        x = 10;
        if (input == 50) {
            x = x + 1;
        } else if (input == 51) {
            x = x * 4;
        } else {
            x = x - 1;
        }
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

