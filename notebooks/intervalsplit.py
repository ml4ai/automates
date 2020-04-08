import numpy as np
import operator
import networkx as nx
import inspect
from model_analysis.networks import GroundedFunctionNetwork as GrFN
from model_analysis.sensitivity import SensitivityAnalyzer

class MaxSensitivity(object):

    def __init__(self, model, bounds, sample_size, method):
        self.model = model
        self.B = bounds
        self.sample_size = sample_size
        self.method = method

    def generate_GrFN(self):
        
        if self.model == "PETASCE":
            tG = GrFN.from_fortran_file(
                f"../tests/data/program_analysis/{self.model}_simple.for"
            )
        else:
            tG = GrFN.from_fortran_file(
                f"../tests/data/program_analysis/{self.model}.for"
            )

        return tG

    def default_split(self, param, partitions=3):

        int_range = self.B[param]
        lower = int_range[0]; upper = int_range[1];
        size = (upper - lower)/partitions

        partition_param_bounds = list()
        for i in range(0, partitions):
            new_upper = lower + size
            partition_param_bounds.append([lower, new_upper])
            lower = new_upper

        return partition_param_bounds

    def split_interval_maxS1(self, param):

        PETPT_GrFN = self.generate_GrFN()
        
        var_max = param
        interval_split = self.B[var_max]

        for  x, y in PETPT_GrFN.node(data='lambda_fn'):
            if y is not None:
                lambda_type = inspect.getsourcelines(y)[0][0].split('def')[1].split('__')[2]
                if lambda_type == 'condition':
                    var = inspect.getsourcelines(y)[0][0]
                    var = var[var.find('(')+1:var.find(')')].split(':')[0]
                    if var == var_max:
                        lambda_fn = inspect.getsourcelines(y)[0][1].split('return')[-1].split('\n')[0]
                        val = lambda_fn[lambda_fn.find('(')+1:lambda_fn.find(')')].split()[-1] 
                        interval_split.append(float(val))

        if len(interval_split) == 2:
            return self.default_split(var_max)

        interval_split = sorted(interval_split)            

        partition_param_bounds = list()
        for i in range(0, len(interval_split)-1):
            if interval_split[i] != interval_split[i+1]:
                partition_param_bounds.append([interval_split[i], interval_split[i+1]])
        
        return partition_param_bounds
        

    def maxS1(self):

        tG = self.generate_GrFN()
        N = self.sample_size

        if self.method == "Sobol":
            (Si, timing_data) = SensitivityAnalyzer.Si_from_Sobol(
                N, tG, self.B, save_time=True
            )
        elif self.method == "FAST":
            (Si, timing_data) = SensitivityAnalyzer.Si_from_FAST(
                N, tG, self.B, save_time=True
            )
        elif self.method == "RBD FAST":
            (Si, timing_data) = SensitivityAnalyzer.Si_from_RBD_FAST(
                N, tG, self.B, save_time=True
            )
        else:
            print("Method not known!")
            exit(0)

        (sample_time, exec_time, analysis_time) = timing_data

        Si =  Si.__dict__ 

        var_names = Si["parameter_list"]
        S1_dict = dict(zip(var_names, Si["O1_indices"].tolist()))

        var_maxS1 = max(S1_dict.items(), key=operator.itemgetter(1))[0]

        return var_maxS1, S1_dict[var_maxS1] 

    
    def search_maxS1(self):

        print("Start Search For Max S1\n")
        var_max, max_val = self.maxS1()
        print(var_max, max_val)
        var_bounds = self.split_interval_maxS1(var_max)
        print(var_bounds)

        return self.search_new_maxS1(var_max, max_val, var_bounds)

    def search_new_maxS1(self, param, val, bounds):

        print("Start Search For New Max S1\n")
        prev_max = val
        print("Starting max values ", param, prev_max)
        for i in range(0, len(bounds)):
            print(f'bound for {param} is {bounds[i]}')
            self.B[param] = bounds[i]
            var_max, max_val = self.maxS1()
            print(f'new max variable is {var_max} and max value is {max_val}')
            if var_max != param:
                var_bounds = self.split_interval_maxS1(var_max)
                print(f'new  bounds for {var_max} are {var_bounds}')
                self.search_new_maxS1(var_max, max_val, var_bounds)

        return


if __name__ == "__main__":

    model = "PETPT"

    bounds = {
        "tmax": [-30.0, 60.0],
        "tmin": [-30.0, 60.0],
        "srad": [0.0, 30.0],
        "msalb": [0.0, 1.0],
        "xhlai": [0.0, 20.0],
    }

    sample_size = 10**5

    method = "Sobol"

    SM = MaxSensitivity(model, bounds, sample_size, method)
    SM.search_maxS1()

