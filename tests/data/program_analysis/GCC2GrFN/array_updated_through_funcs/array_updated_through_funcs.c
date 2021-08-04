
/*
    Represents an array / pointer being passed through many functions,
    and only updated in the largest scoped call. This change should be
    represented in our GrFN dataflow represention and a new version should
    flow all the way back to the root container.
*/

void func_3(int l_3[])
{
    // Input func_3::l_3::1
    if (l_3[0] == 1)
    {
        // Input func_2.IF_0_0::l_3::1
        l_3[0] = 1111;
        // Output func_2.IF_0_0::l_3::2
    }
    else
    {
        l_3[0] = 2222;
        // Output func_2.IF_0_1::l_3::3
    }
    // Output func_3::l_3::2
}

void func_2(int l_2[])
{
    // Input func_2::l_2::1
    func_3(l_2);
    // Output func_2::l_2::2
}

void func_1(int l_1[])
{
    // Input func_1::l_1::1
    func_2(l_1);
    // Output func_1::l_1::2
}

int main()
{
    int l[5] = {1, 2, 3, 4, 5};
    // Input l::1
    func_1(l);
    // Output l::2
    return l[0];
}