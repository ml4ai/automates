int main()
{
    // Use variables for constants, otherwise gcc collapses constants
    int one = 1;
    int two = 2;
    int three = 3;
    int four = 4;

    int div = two / four;
    int mult = two * three;
    int remainder = two % three;

    int add = one + two;
    int sub = one - two;

    // should become 2
    int bitwise_l_shift = one << 1;
    // should become 1
    int bitwise_r_shift = two >> 1;

    int lt = one < two;
    int lte = one <= two;
    int gt = one > two;
    int gte = one >= two;

    int eq = one == two;
    int neq = one != two;

    // should be 0
    int bitwise_and = one & two;
    int bitwise_xor = one ^ two;
    // should be 3
    int bitwise_or = one | two;

    int zero = 0;
    // int logical_and = one && zero;
    // int logical_or = one || zero;

    return 0;
}