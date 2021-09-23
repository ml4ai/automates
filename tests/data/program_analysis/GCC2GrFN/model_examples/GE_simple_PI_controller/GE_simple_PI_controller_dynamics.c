#include <stdio.h>

double integrator_state = 0.0;

/*
 * Simplified version of the T-MATS Simple PI controller library block
 */
double PI_calc(double Input_dmd, double Input_sensed, double Kp_M, double Ki_M, double timestep)
{
    double error = Input_dmd - Input_sensed;

    integrator_state = integrator_state + timestep * error;

    return error * Kp_M + integrator_state * Ki_M;
}

/*
 * Proportional plant!
 */
double plant_model(double input, double gain)
{
    return input * gain; //10 --> since gain 0.01, input must be 1000
}

int main(int argc, char **argv)
{

    double t_final = 100.5;
    double time_step = 0.015;

    double Ki_M = 20.0;
    double Kp_M = 75.0;

    int num_steps = t_final / time_step;

    double desired_output = 10.0;

    double plant_command;
    double sensed_output;

    double plant_gain = 0.01;

    sensed_output = 0.0;

    plant_command = PI_calc(desired_output, sensed_output, Kp_M, Ki_M, time_step);

    sensed_output = plant_model(plant_command, plant_gain);
}