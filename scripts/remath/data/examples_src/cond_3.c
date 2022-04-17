#include<stdio.h>

int main()
{
	int x=1;
	int y=2;
	if (x < y)	//test-condition
	{
	  if (x > 0)
	  {
		  x = y;
		}
	}
	else
	{
	  x = 9;
	}
	printf("Answer %d\n", x);
	return 0;
}