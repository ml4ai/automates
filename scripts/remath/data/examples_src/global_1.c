#include<stdio.h>

int g = 2;

int fun1(int x)
{
  int y = x + g;
  return y;
}

int main()
{
	int x;
	g = g + 2;
	int y = 1;
	x = fun1(y);
	printf("Answer %d\n", x);
	return 0;
}
