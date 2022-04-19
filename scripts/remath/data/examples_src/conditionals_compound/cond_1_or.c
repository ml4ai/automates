int main() {

    int v_or = 10;
    int x = 10;
    int y = 20;
    int if_clause = 1;
    int else_clause = 2;

    // compound conditional: disjunction
    if (x < v_or || y > v_or) {
        x = if_clause;
    } else {
        x = else_clause;
    }

    return x;
}