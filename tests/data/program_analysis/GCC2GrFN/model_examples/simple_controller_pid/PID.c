#include <stdio.h>

struct _pid
{
	float SetSpeed;
	float ActualSpeed;
	float err;
	float err_last;
	float Kp, Ki, Kd;
	float voltage;
	float integral;
} pid;

// int test = 10;

void PID_init()
{
	printf("PID_init begin \n");
	pid.SetSpeed = 0.0;
	pid.ActualSpeed = 0.0;
	pid.err = 0.0;
	pid.err_last = 0.0;
	pid.voltage = 0.0;
	pid.integral = 0.0;
	pid.Kp = 0.2;
	pid.Ki = 0.015;
	pid.Kd = 0.2;
	printf("PID_init end \n");
}

float PID_realize(float speed)
{
	pid.SetSpeed = speed;
	pid.err = pid.SetSpeed - pid.ActualSpeed;
	pid.integral += pid.err;
	pid.voltage = pid.Kp * pid.err + pid.Ki * pid.integral + pid.Kd * (pid.err - pid.err_last);
	pid.err_last = pid.err;
	pid.ActualSpeed = pid.voltage * 1.0;
	return pid.ActualSpeed;
}

int main()
{
	printf("System begin \n");
	PID_init();
	int count = 0;
	while (count < 100)
	{
		float speed = PID_realize(20.0);
		printf("%f\n", speed);
		count++;
	}
	// printf("count: %d\n", count);
	// printf("SetSpeed: %f\n", pid.SetSpeed);
	// printf("ActualSpeed: %f\n", pid.ActualSpeed);
	// printf("err: %f\n", pid.err);
	// printf("err_last: %f\n", pid.err_last);
	// printf("voltage: %f\n", pid.voltage);
	// printf("integral: %f\n", pid.integral);
	// printf("Kp: %f\n", pid.Kp);
	// printf("Ki: %f\n", pid.Ki);
	// printf("Kd: %f\n", pid.Kd);
	return 0;
}
