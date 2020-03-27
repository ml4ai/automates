import numpy as np
import pandas as pd
from model_analysis.networks import GroundedFunctionNetwork as GrFN
from model_analysis.sensitivity import SensitivityIndices, SensitivityAnalyzer
from model_analysis.visualization import SensitivityVisualizer


class SensitivityModel(object):
    def __init__(self, model, bounds, sample_list, method):
        self.model = model
        self.B = bounds
        self.sample_list = sample_list
        self.method = method

    def sensitivity(self, N):

        if self.model == "PETASCE":
            # tG = GrFN.from_fortran_file(f"../../tests/data/program_analysis/{self.model}_simple.for", save_file=True)
            tG = GrFN.from_fortran_file(
                f"../tests/data/program_analysis/{self.model}_simple.for"
            )
        else:
            # tG = GrFN.from_fortran_file(f"../../tests/data/program_analysis/{self.model}.for", save_file=True)
            tG = GrFN.from_fortran_file(
                f"../tests/data/program_analysis/{self.model}.for"
            )

        if self.method == "Sobol":
            (sobol_dict, timing_data) = SensitivityAnalyzer.Si_from_Sobol(
                N, tG, self.B, save_time=True
            )
        elif self.method == "FAST":
            (sobol_dict, timing_data) = SensitivityAnalyzer.Si_from_FAST(
                N, tG, self.B, save_time=True
            )
        elif self.method == "RBD FAST":
            (sobol_dict, timing_data) = SensitivityAnalyzer.Si_from_RBD_FAST(
                N, tG, self.B, save_time=True
            )
        else:
            print("Method not known!")
            exit(0)

        (sample_time, exec_time, analysis_time) = timing_data

        return sobol_dict.__dict__, sample_time, exec_time, analysis_time

    def generate_dataframe(self):

        i = len(self.sample_list) - 1
        N = self.sample_list[i]
        Si = self.sensitivity(N)[0]
        var_names = Si["parameter_list"]
        S1_max = dict(zip(var_names, Si["O1_indices"].tolist()))
        ST_max = dict(zip(var_names, Si["OT_indices"].tolist()))

        df_S1 = pd.DataFrame.from_dict(
            S1_max, orient="index", columns=[self.model]
        )
        df_ST = pd.DataFrame.from_dict(
            ST_max, orient="index", columns=[self.model]
        )

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

            # S2_dataframe = pd.DataFrame(data=Si['O2_indices'], columns=var_names)
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
            # S1.show()
            return

        if component == "S2":
            if self.method == "Sobol":
                S2 = plots.create_S2_plot()
                # S2.show()
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

<<<<<<< HEAD

    sample_list = [10**x for x in range(2, 3)]

    method = 'Sobol'

=======
    method = "Sobol"
>>>>>>> 24b88276b3779d306b786e914127bc859bf37395

    SM = SensitivityModel(model, bounds, sample_list, method)

    SM.generate_dataframe()

    indices_lst = SM.generate_indices()

    component = "S1"
    SM.sensitivity_plots(indices_lst, component)

    component = "S2"
    SM.sensitivity_plots(indices_lst, component)

    component = "runtime"
    SM.sensitivity_plots(indices_lst, component)
