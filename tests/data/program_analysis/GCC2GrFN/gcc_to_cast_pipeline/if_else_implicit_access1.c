int func() {

    int x = 0;
    int y = 3;

    if (x == 0) {
        y = x + 1;
        int z = y*x;
    }
    else {
        int z = x*2;
    }
    // decision for y at the end is between updated version along if branch
    // and original version along else branch
    // --> the else branch has an "implicit access" which is not reflected in the code
    // --> y is accessed before modified along the else branch, so it should come in the top
    //     interface

    return y;
}

int main() {
    int w = 0;
    for (int i = 0; i < 3; ++i) {
        w = func();
    }

    return w;
}


