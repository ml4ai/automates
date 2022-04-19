int main() {

    int v_and = 10;
    int x = 10;
    int y = 20;
    int if_clause = 1;
    int else_clause = 2;

    // compound conditional: conjunction
    if (x < v_and && y > v_and) {
        x = if_clause;
    } else {
        x = else_clause;
    }

    return x;
}