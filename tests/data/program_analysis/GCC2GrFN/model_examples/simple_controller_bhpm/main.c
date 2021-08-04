/*
 * File: main.c
 * Created Date: Friday April 2nd 2021
 * Author: Steven Atkinson (steven.atkinson1@ge.com)

 * Modified Date: Friday April 22nd 2021
 * Author: Piyush Pandita (steven.atkinson1@ge.com)
 */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "generator.h"

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
