/*
 * File: generator.h
 * Created Date: Friday April 2nd 2021
 * Author: Steven Atkinson (steven.atkinson1@ge.com)
 */

void generate_normal(float vec[], int samples);

void generate_uniform(float vec[], int samples);

void generate_arange(float vec[], int samples);

void generate_signal(float vec[], float dt, int steps);