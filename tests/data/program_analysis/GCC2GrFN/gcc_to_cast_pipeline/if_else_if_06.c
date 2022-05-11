// Stripped down version of PI_calc from Abha's example (GE_simple.c)
double h = 1100.0;
double i = 0.0;
double j = 0.0;

double func(double a, double b, double c, double d, double e)
{
    double g = a - b;
	double u;
    int f = 1; 
    
	u = g*c + (j + e*g)*d;
	if (u > h)
	{
		u = h; 
		if (g > 0) 
		{
		    f = 0;
		};
	}
	else if (u < i) 
	{
		u = i;
		if (g < 0)
		{
			f = 0;
		};
	};
	if (f)
	{
		j = j + e*g;
	}
    return u;

}

int main()
{
    int y = func(1000, 1000, 1000, 1000, 1000);
    return y;
}
