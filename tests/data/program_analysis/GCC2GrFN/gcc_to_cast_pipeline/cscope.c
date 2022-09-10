int g = 0;
int func(int x){
   g = g + x;
   return g*2;
}
int main() {
   int i = 0;
   int z;
   while (i < 10) {
      z = func(i);
      i = i + 1;
    }
   return z;
}

