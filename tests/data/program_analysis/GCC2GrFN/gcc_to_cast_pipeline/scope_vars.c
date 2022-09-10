int g = 200;

int func()
{
   int y = 100;
   int x = 20;

   if (y > 10){
      x = x + 1;
      g = g + x;
  }
   else if (y < 0) {
      x = x - 1;
      g = g + y;
   }
   else {
      x = 0;
   }
   return x;

}

int main(){
    int z;
    g = g + 10;
    z = func();
    g = g + 20;
}
