import os
import numpy as np
import pandas as pd
import pytest
from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_analysis.sensitivity import SensitivityAnalyzer
from automates.model_analysis.visualization import SensitivityVisualizer


@pytest.fixture
def sensitivity_visualizer():

    N = [10, 100, 1000, 10000]
    tG = GroundedFunctionNetwork.from_json("tests/data/model_analysis/PT_GrFN.json")
    var_bounds = {
        "PETPT::petpt::tmax::-1": [-30.0, 60.0],
        "PETPT::petpt::tmin::-1": [-30.0, 60.0],
        "PETPT::petpt::srad::-1": [0.0, 30.0],
        "PETPT::petpt::msalb::-1": [0.0, 1.0],
        "PETPT::petpt::xhlai::-1": [0.0, 20.0],
    }

    sensitivity_indices_lst = []

    var_names = var_bounds.keys()

    for i in range(len(N)):
        (Si_list, timing_data) = SensitivityAnalyzer.Si_from_Sobol(
            N[i], tG, var_bounds, save_time=True, I={}
        )
        Si = Si_list[0]
        (sample_time, exec_time, analysis_time) = timing_data
        sobol_dict = Si.__dict__
        S1_dict = dict(zip(var_names, sobol_dict["O1_indices"].tolist()))

        for k in range(sobol_dict["O2_indices"].shape[0]):
            for l in range(k, sobol_dict["O2_indices"].shape[1]):
                if k != l:
                    sobol_dict["O2_indices"][l][k] = sobol_dict["O2_indices"][k][l]

        sobol_dict["O2_indices"] = np.nan_to_num(sobol_dict["O2_indices"]).tolist()

        S2_dataframe = pd.DataFrame(data=sobol_dict["O2_indices"], columns=var_names)

        sobol_dict_visualizer = {
            "sample size": np.log10(N[i]),
            "S1": S1_dict,
            "S2": S2_dataframe,
            "sampling time": sample_time,
            "execution time": exec_time,
            "analysis time": analysis_time,
        }

        sensitivity_indices_lst.append(sobol_dict_visualizer)

    yield SensitivityVisualizer(sensitivity_indices_lst)


def test_sensitivity_visualization(sensitivity_visualizer):
    sensitivity_visualizer.create_S1_plot()
    sensitivity_visualizer.create_S2_plot()
    sensitivity_visualizer.create_clocktime_plot()
    # Cleanup actions
    os.remove("s1_plot.pdf")
    os.remove("s2_plot.pdf")
    os.remove("clocktime_plot.pdf")
