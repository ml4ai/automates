int z = 0;

void increment_z() {
    z = z + 1;
}

int main() {
    int x = 1;

    if (x == 1) {
        increment_z();
    }
    else {
        increment_z();
    }
    // z should have value 1

    return z;
}


    
