#include <stdio.h>
#include "generator.h"
#include <math.h>
#include <stdlib.h>
#define PI 3.142
#define clip 0.000001

void generate_normal(float vec[], int samples)
{
    float u_1;
    float u_2;
    for (int i = 0; i < samples; i++)
    {
        u_1 = rand() % 50;
        u_2 = rand() % 50;
        vec[i] = sqrt(-2.0 * log(u_1 / 50.0 + clip)) * cos(2.0 * PI * u_2 / 50.0);
        vec[i + 1] = sqrt(-2.0 * log(u_1 / 50.0 + clip)) * sin(2.0 * PI * u_2 / 50.0);
        i = i + 1;
    }
}

void generate_uniform(float vec[], int samples)
{
    float u_1;
    float u_2;
    for (int i = 0; i < samples; i++)
    {
        u_1 = rand() % 50;
        u_2 = rand() % 50;
        vec[i] = 2.0 * PI * u_1 / 50.0;
        vec[i + 1] = 2.0 * PI * u_2 / 50.0;
        i = i + 1;
    }
}

void generate_arange(float vec[], int samples)
{
    for (int i = 0; i < samples; i++)
    {
        vec[i] = i;
    }
}

void generate_signal(float vec[], float dt, int steps)
{
    float theta[steps];
    float w[steps];
    float tau[steps];
    float x[steps];
    float t[steps];
    float coef;

    coef = 1.0 / sqrt(steps);

    generate_normal(theta, steps);

    generate_normal(w, steps);

    generate_uniform(tau, steps);

    generate_arange(t, steps);

    for (int i = 0; i < steps; i++)
    {
        float sum_sig = 0.0;
        for (int j = 0; j < steps; j++)
        {
            sum_sig = sum_sig + -1.0 * w[j] * pow(theta[j], 2) * sin(theta[j] * t[i] + tau[j]);
        }
        vec[i] = coef * sum_sig;
    }
}

int main()
{

    float err = 0.1;
    float err_last = 0.0;
    float integral = 0.0;
    float integral_last = 0.1;
    float Kp = 0.7;
    float Ki = 0.15;
    float Kd = 0.4;
    float dt = 0.01;
    int n_steps = 4096;
    float voltage[n_steps];

    float x[n_steps];

    // srand(time(0));
    generate_signal(x, dt, n_steps);

    /* This runs the step-wise PID control output */
    for (int i = 0; i < n_steps; i++)
    {
        err = x[i];
        integral = integral_last + (err - err_last) * dt * 0.5;

        voltage[i] = -1.0 * Kp * err - 1.0 * Ki * integral - 1.0 * Kd * (err - err_last);
        err_last = err;
        integral_last = integral;

        printf("%f\n", voltage[i]);
    }
    return 0;
}
