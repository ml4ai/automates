import numpy as np
import operator
import inspect
from src.model_analysis.networks import GroundedFunctionNetwork as GrFN
from src.model_analysis.sensitivity import SensitivityAnalyzer
from copy import deepcopy
from collections import deque
import matplotlib.pyplot as plt
from matplotlib import cm
from collections import OrderedDict
import networkx as nx
import os
import json
import csv
import pandas as pd
import ast

class MaxSensitivity(object):

    def __init__(self, model, bounds, sample_size, method):
        self.model = model
        self.B = bounds
        self.sample_size = sample_size
        self.method = method


    def generate_GrFN(self):

        if self.model == "PETASCE":
            tG = GrFN.from_fortran_file(
                f"../../tests/data/program_analysis/{self.model}_simple.for"
            )
        else:
            tG = GrFN.from_fortran_file(
                f"../../tests/data/program_analysis/{self.model}.for"
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

    def split_interval_S1(self, param):

        PETPT_GrFN = self.generate_GrFN()

        var_max = param
        interval_split = deepcopy(self.B[var_max])

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

    def S1(self):

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

        return S1_dict

    def maxS1(self, S1_dict):

        var_maxS1 =  max(S1_dict.items(), key=operator.itemgetter(1))[0]
        return  var_maxS1, S1_dict[var_maxS1]


class Node:

    def __init__(self, val):
        self.val = val
        self.par = None
        self.child  = list()
        self.index = None
        self.key =  dict()


class MaxSensitivityTree(object):

    def __init__(self):

        self.root = None

    def is_empty(self):

        return self.root == None


    def construct_tree(self, model, B, N, method):

        sensitivity = MaxSensitivity(model, B, N, method)
        
        root_val = sensitivity.S1()

        root_varmax, root_maxS1 = sensitivity.maxS1(root_val)

        root_bounds = sensitivity.B[root_varmax]

        self.root = Node(root_val)
        
        self.root.key = {root_varmax:root_bounds}

        child_bounds = sensitivity.split_interval_S1(root_varmax)

        return self.create_child(sensitivity, self.root, child_bounds, 0)


    def create_child(self, S1_obj, param, bounds, pass_number, max_iterations=5):
        
        if pass_number == max_iterations:
            return

        param_dict = param.val
        param_varmax, param_maxS1 = S1_obj.maxS1(param_dict)  
    
        if param != self.root:
            param_par_varmax, param_par_maxS1 = S1_obj.maxS1(param.par.val)

        if len(bounds)==1 and param_varmax == param_par_varmax:
            return


        for i in range(0, len(bounds)):
            S1_obj.B[param_varmax] =  bounds[i]

            new_dict = S1_obj.S1()
            new_param_varmax, new_param_maxS1 = S1_obj.maxS1(new_dict)
            new_param = Node(new_dict)
            param.child.append(new_param)
            new_param.par = param
            new_param.key = {param_varmax:bounds[i]}
            if param_varmax != new_param_varmax:
                new_param_bounds = S1_obj.split_interval_S1(new_param_varmax)
                self.create_child(S1_obj, new_param, new_param_bounds, pass_number+1)

        return

    def create_graph(self, filename, file_format=None):
        
        if filename.split('.')[1] == 'json':
            file_format = 'json'
        elif filename.split('.')[1] == 'csv':
            file_format = 'csv'
        else:
            print('File format not supported!')
            return

        G = nx.DiGraph()

        if self.root is None:
            print("Tree is empty!")
            return

        qu = deque()
        qu.append(self.root)
        node_no = 0

        while len(qu):
            p = qu.popleft()
            node_no += 1
            p.index = node_no
            val = p.val
            var =  max(val.items(), key=operator.itemgetter(1))[0]
            self.toFile(p, filename, file_format)
            if p == self.root:
                G.add_node(p.index, rank=0, label=str((node_no, var, p.key)))
            else:
                G.add_node(p.index, label=str((node_no, var)))
            if p != self.root:
                G.add_edges_from([(p.par.index, p.index)], color='red', label=str(p.key))
            if p.child is not None:
                for i in range(0, len(p.child)):
                    qu.append(p.child[i])
       
        G.graph['graph'] = {'rankdir':'TD'}
        G.graph['node']={'shape':'circle'}
        G.graph['edges']={'arrowsize':'4.0'}

        A = nx.nx_agraph.to_agraph(G)

        return A

    def plot(self, A, filename):
        A.layout('dot')
        A.draw(filename + '.png')


    def toFile(self, node, filename, file_format):

        data =  {"node":node.index, "S1 indices":node.val}

        if file_format == 'json':

            a = []

            if not os.path.isfile(filename):
                a.append(data)
                with  open(filename, 'w') as f:
                    f.write(json.dumps(a, indent=2))
            else:
                with open(filename) as fjson:
                    js_data =  json.load(fjson)

                js_data.append(data)
                with  open(filename, 'w') as f:
                    f.write(json.dumps(js_data,  indent=2))

        elif file_format  == 'csv':
            
            if not os.path.isfile(filename):
                with open(filename, 'a') as f:
                    writer = csv.DictWriter(f, fieldnames=["node", "S1 indices"])
                    writer.writeheader()
                    writer.writerow(data)
            else:
                with open(filename, 'a') as f:
                    writer = csv.DictWriter(f, fieldnames=["node", "S1 indices"])
                    writer.writerow(data)


    def bar_plot_from_file(self, node_number, filepath):

        file_ext = filepath.split('.')[1]
        filename = filepath.split('.')[0]

        if file_ext ==  'json':
            with open(filepath, 'r') as f:
                data = json.load(f)

            for item in data:
                if item['node'] == node_number:
                    self.bar(item['node'], item['S1 indices'], filename)

        elif file_ext == 'csv':
            df = pd.read_csv(filepath)
            val = df[df['node'] == node_number]['S1 indices'].values[0]
            val = ast.literal_eval(val)
            self.bar(node_number, val, filename)

    def bar(self, node_number, S1_dict, filename):
        
        sorted_dict = OrderedDict(sorted(S1_dict.items(), key=lambda t: t[1]))

        xval = range(len(sorted_dict)); yval = list(sorted_dict.values());
        colors = cm.Accent(np.array(yval) / max(yval))
        plot = plt.scatter(yval, yval, c=yval, cmap='Accent')
        plt.clf()
        plt.colorbar(plot)
        plt.bar(xval, yval, color=colors, align='center')
        plt.xticks(xval, list(sorted_dict.keys()))
        plt.xlabel('Parameters')
        plt.ylabel('S1 indices')
        plt.title(f'Bar Plot of S1 indices for Node - {node_number}')
        plt.savefig(filename + '_barplot.png')


