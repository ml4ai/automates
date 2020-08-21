import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from penman import SensitivityModel

class ModelCompareS2(object):

    def __init__(self, model1, model2, B1, B2, sample_list):
        
        self.model1 = model1
        self.model2 = model2
        self.B1 = B1
        self.B2 = B2
        self.sample_list = sample_list


    def compare(self, method='Sobol', *args, **kwargs):

        SM1 = SensitivityModel(self.model1, self.B1, self.sample_list, method)
        SM2 = SensitivityModel(self.model2, self.B2, self.sample_list, method)

        indices_lst1 = SM1.generate_indices()
        indices_lst2 = SM2.generate_indices()

        var1_names = indices_lst1[0]['S1'].keys()
        var2_names = indices_lst2[0]['S1'].keys()

        # var1_names, indices_lst1 = self.B1.keys(), SM1.generate_indices()
        # var2_names, indices_lst2 = self.B2.keys(), SM2.generate_indices()

        shared_vars = [name for name in var2_names if name in var1_names and name in var1_names]
        non_shared_var1 = [name for name in var1_names if name not in var2_names]
        non_shared_var2 = [name for name in var2_names if name not in var1_names]


        for i in range(len(self.sample_list)):
            S2_var1_dataframe = indices_lst1[i]['S2']
            S2_var1_dataframe[S2_var1_dataframe < 0 ] = 0
            S2_var1_dataframe[self.model1] = var1_names
            S2_var1_dataframe.set_index(self.model1, inplace=True)

            S2_var2_dataframe = indices_lst2[i]['S2']
            S2_var2_dataframe[S2_var2_dataframe < 0 ] = 0
            S2_var2_dataframe[self.model2] = var2_names
            S2_var2_dataframe.set_index(self.model2, inplace=True)


            S2_var1_shared = S2_var1_dataframe.loc[shared_vars, shared_vars]
            S2_var1_non_shared = S2_var1_dataframe.loc[non_shared_var1, var1_names]

            S2_var2_shared = S2_var2_dataframe.loc[shared_vars, shared_vars]
            S2_var2_non_shared = S2_var2_dataframe.loc[non_shared_var2, var2_names]

            fig = plt.figure(figsize=(15,10))

            ax1 = fig.add_subplot(221)
            ax2 = fig.add_subplot(222)

            cmap1 = sns.light_palette("green")
            cmap2 = sns.light_palette("purple")
            cmap3 = sns.light_palette("blue")

            max_val1 = max(S2_var1_dataframe.max(axis=0).values)
            max_val2 = max(S2_var2_dataframe.max(axis=0).values)

            min_val1 = min(S2_var1_dataframe.min(axis=0).values)
            min_val2 = min(S2_var2_dataframe.min(axis=0).values)

            max_val = max(max_val1, max_val2)
            min_val = min(min_val1, min_val2)


            mask = np.triu(np.ones_like(S2_var1_shared, dtype=np.bool))
            g = sns.heatmap(S2_var1_shared, mask=mask, cmap = cmap1, annot=True, xticklabels = shared_vars, 
                    yticklabels=shared_vars, annot_kws={"fontsize":10}, norm =
                    Normalize(), ax=ax1, square=True, 
                    linewidth=0.5, cbar_kws={"shrink": .5},
                    vmax=max_val,
                    vmin=min_val)

            mask = np.triu(np.ones_like(S2_var2_shared, dtype=np.bool))
            g = sns.heatmap(S2_var2_shared, mask=mask, cmap = cmap1, annot=True, xticklabels = shared_vars, 
                    yticklabels=shared_vars, annot_kws={"fontsize":10}, norm =
                    Normalize(), ax=ax2, square = True, 
                    linewidth=0.5, cbar_kws={"shrink": .5},
                    vmax=max_val,
                    vmin=min_val)

            if len(S2_var1_non_shared.values) != 0:

                ax3 = fig.add_subplot(223)
                g = sns.heatmap(S2_var1_non_shared, cmap = cmap2, annot=True,
                        annot_kws={"fontsize":10}, norm = Normalize(), ax=ax3,
                        square=True, 
                        linewidth=0.5, cbar_kws={"shrink": .5},
                        vmax=max_val,
                        vmin=min_val)

            if len(S2_var2_non_shared.values) != 0:

                ax4 = fig.add_subplot(224)
                g = sns.heatmap(S2_var2_non_shared, cmap = cmap3, annot=True,
                        annot_kws={"fontsize":10}, norm = Normalize(), ax=ax4,
                        square=True, 
                        linewidth=0.5, cbar_kws={"shrink": .5},
                        vmax=max_val,
                        vmin=min_val)

            fig.suptitle('$S_{ij} ( log_{10}N = $' + str(np.log10(self.sample_list[i])) + '$ )$', fontsize = 30)
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            plt.show()
      


if __name__ == '__main__':

    B1 = {
        'tmax':[-30.0, 60.0],
        'tmin':[-30.0, 60.0],
        'srad': [0.0, 30.0],
        'msalb': [0.0, 1.0],
        'xhlai': [0.0, 20.0]
    }

    B2 = {
        'tmax':[-30.0, 60.0],
        'tmin':[-30.0, 60.0],
        'srad': [0.0, 30.0],
        'msalb': [0.0, 1.0],
        'xhlai': [0.0, 20.0],
        'tavg': [-30, 60],
        'tdew': [-30, 60],
        'windsp': [0.0, 10.0],
        'clouds': [0.0, 1.0]
    }
                            ### ---- Model Comparison Results ---- ###
    comparePET = ModelCompareS2('PETPT', 'PETPNO', B1, B2, [10**x for x in range(1, 2)])
    comparePET.compare()



