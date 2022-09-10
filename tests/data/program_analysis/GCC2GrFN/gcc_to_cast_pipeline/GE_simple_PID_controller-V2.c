#include <stdio.h>

double integrator_state = 0.0;
double derv = 0.0;
double error_last = 0.0;

/*
 * Simplified version of the T-MATS Simple PI controller library block
 */
double PID_calc(double Input_dmd, double Input_sensed, double Kp_M, double Ki_M, double Kd_M, double timestep)
{
  double error = Input_dmd - Input_sensed;
    
  integrator_state = integrator_state + timestep*error;
  derv = error - error_last;
  error_last = error;
  return error*Kp_M + integrator_state*Ki_M + derv*Kd_M;
}

/*
 * Proportional plant!
 */
double plant_model(double input, double gain)
{
  return input*gain; //10 --> since gain 0.01, input must be 1000
}

int main(int argc, char **argv)
{

  double t_final = 100.5;
  double time_step = 0.015;
  
  double Ki_M = 20.0;
  double Kp_M = 75.0;
  double Kd_M = 10.0;
	
  int num_steps = t_final / time_step;
    	
  double desired_output = 10.0;
	
  double plant_command;
  double sensed_output;
	
  double plant_gain = 0.01;

  sensed_output = 0.0;

  //FILE *fptr;
  //fptr = fopen("C:\\Users\\200015853\\Downloads\\output_data.txt","w");

  for (int i = 0; i < num_steps; i++)
    {
      plant_command = PID_calc(desired_output, sensed_output, Kp_M, Ki_M, Kd_M, time_step);
		
      sensed_output = plant_model(plant_command, plant_gain);

      //fprintf(fptr,"%f, %f, %f\n", (double)i*time_step, plant_command, sensed_output);
      printf("%f, %f, %f, %f\n", (double)i*time_step, plant_command, sensed_output, derv);
    }

  //fclose(fptr);

  return 0;
}
