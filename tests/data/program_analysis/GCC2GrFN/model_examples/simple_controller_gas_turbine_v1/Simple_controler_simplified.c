#include <stdio.h>

double MAJOR_TIMESTEP = .01;

int Integrator_IWORK = 1;
int Integrator_CSTATE = 3;

/*
 * Simplified version of the T-MATS Simple PI controller library block
 */
double simple_step(double Input_dmd, double Input_sensed, double timestep)
{

    if (Integrator_IWORK != 0)
    {
        Integrator_CSTATE = 3;
    }

    double add1 = Input_dmd - Input_sensed;
    double Ki_M = 0.1 / 2;
    double usumJi1 = add1 * Ki_M;

    double Kp_M = 0.05 / 2;
    double gain1 = add1 * Kp_M;
    double Effector_Demand = gain1 + Integrator_CSTATE;

    if (timestep == MAJOR_TIMESTEP)
    {
        Integrator_IWORK = 0;
    }

    return Effector_Demand;
}

int main(int argc, char **argv)
{

    double t_final = 10.5;
    double time_step = 0.015;
    int num_steps = t_final / time_step;
    double time_step_results[num_steps];

    for (int i = 0; i < num_steps; i++)
    {
        time_step_results[i] = simple_step(10, 2, i * time_step);
    }

    // for (int i = 0; i < num_steps; i++)
    // {
    //     printf("%d: %f\n", i, time_step_results[i]);
    // }

    return 0;
}
