import numpy as np
import pandas as pd
from model_analysis.networks import GroundedFunctionNetwork as GrFN
from model_analysis.sensitivity import SensitivityIndices, SensitivityAnalyzer
from model_analysis.visualization import SensitivityVisualizer


class SensitivityModel(object):
    def __init__(self, model: GrFN, bounds, sample_list, method, model_name = "model"):
        self.model = model
        self.model_name = model_name
        self.bounds = bounds
        self.sample_list = sample_list
        self.method = method

    def set_bounds(self, bounds):
        self.bounds = bounds

    def modify_bounds(self, param, partition, partitions=3):

        partition -= 1
        if partition < 0 or partition > partitions:
            raise ValueError("Invalid partition number!")

        int_range = self.bounds[param]
        lower = int_range[0]
        upper = int_range[1]
        size = (upper - lower) / partitions

        partition_param_bounds = list()
        for i in range(0, partitions):
            new_upper = lower + size
            partition_param_bounds.append([lower, new_upper])
            lower = new_upper

        self.bounds[param] = partition_param_bounds[partition]

    def sensitivity(self, N):

        if self.method == "Sobol":
            (sobol_dict, timing_data) = SensitivityAnalyzer.Si_from_Sobol(
                N, self.model, self.bounds, save_time=True
            )
        elif self.method == "FAST":
            (sobol_dict, timing_data) = SensitivityAnalyzer.Si_from_FAST(
                N, self.model, self.bounds, save_time=True
            )
        elif self.method == "RBD FAST":
            (sobol_dict, timing_data) = SensitivityAnalyzer.Si_from_RBD_FAST(
                N, self.model, self.bounds, save_time=True
            )
        else:
            print("Method not known!")
            exit(0)

        (sample_time, exec_time, analysis_time) = timing_data

        return sobol_dict.__dict__, sample_time, exec_time, analysis_time

    def generate_dataframes(self, decimal=2):

        i = len(self.sample_list) - 1
        N = self.sample_list[i]
        Si = self.sensitivity(N)[0]
        var_names = Si["parameter_list"]
        S1_max = dict(zip(var_names, Si["O1_indices"].tolist()))
        ST_max = dict(zip(var_names, Si["OT_indices"].tolist()))

        df_S1 = pd.DataFrame.from_dict(
            S1_max, orient="index", columns=[self.model_name]
        )
        df_ST = pd.DataFrame.from_dict(
            ST_max, orient="index", columns=[self.model_name]
        )

        df_S1 = df_S1.round(decimal).T
        df_ST = df_ST.round(decimal).T

        return df_S1, df_ST

    def generate_indices(self):

        sobol_indices_lst = list()

        for i in range(len(self.sample_list)):
            N = self.sample_list[i]
            Si, sample_time, exec_time, analysis_time = self.sensitivity(N)
            var_names = Si["parameter_list"]
            S1_dict = dict(zip(var_names, Si["O1_indices"].tolist()))

            if self.method == "Sobol":

                for k in range(Si["O2_indices"].shape[0]):
                    for l in range(k, Si["O2_indices"].shape[1]):
                        if k != l:
                            Si["O2_indices"][l][k] = Si["O2_indices"][k][l]

                Si["O2_indices"] = np.nan_to_num(Si["O2_indices"]).tolist()
            else:
                Si["O2_indices"] = None

            S2_dataframe = pd.DataFrame(
                data=Si["O2_indices"], columns=Si["parameter_list"]
            )

            sobol_dict = {
                "sample size": self.sample_list[i],
                "S1": S1_dict,
                "S2": S2_dataframe,
                "sampling time": sample_time,
                "execution time": exec_time,
                "analysis time": analysis_time,
            }

            sobol_indices_lst.append(sobol_dict)

        return sobol_indices_lst

    def sensitivity_plots(self, indices_lst, component):

        plots = SensitivityVisualizer(indices_lst)

        if component == "S1":
            S1 = plots.create_S1_plot()
            S1.show()
            return

        if component == "S2":
            if self.method == "Sobol":
                S2 = plots.create_S2_plot()
                S2.show()
                return

        if component == "runtime":
            runtime = plots.create_clocktime_plot()
            # runtime.show()
            return


if __name__ == "__main__":

    # model = 'PETASCE'
    model = "PETPT"

    bounds = {
        "tmax": [-30.0, 60.0],
        "tmin": [-30.0, 60.0],
        "srad": [0.0, 30.0],
        "msalb": [0.0, 1.0],
        "xhlai": [0.0, 20.0],
    }

    # bounds = {
    # "doy": [1, 365],
    # "meevp": [0, 1],
    # "msalb": [0, 1],
    # "srad": [1, 30],
    # "tmax": [-30, 60],
    # "tmin": [-30, 60],
    # "xhlai": [0, 20],
    # "tdew": [-30, 60],
    # "windht": [0.1, 10],
    # "windrun": [0, 900],
    # "xlat": [3, 12],
    # "xelev": [0, 6000],
    # "canht": [0.001, 3],
    # }

    sample_list = [10 ** x for x in range(1, 6)]

    method = "Sobol"

    SM = SensitivityModel(model, bounds, sample_list, method)

    param = "tmax"
    partitions = 3
    partition = 2
    SM.modify_bounds(param, partition, partitions)

    # df_S1, df_ST = SM.generate_dataframe(4)
    # print("df_ST\n", df_ST)
    # print("df_S1\n", df_S1)

    indices_lst = SM.generate_indices()

    component = "S1"
    SM.sensitivity_plots(indices_lst, component)

    # component = "S2"
    # SM.sensitivity_plots(indices_lst, component)

    # component = "runtime"
    # SM.sensitivity_plots(indices_lst, component)
