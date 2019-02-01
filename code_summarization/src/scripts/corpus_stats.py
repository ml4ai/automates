import pickle
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from tqdm import tqdm

import utils.utils as utils

deep_learning = ["mxnet", "tensorflow", "theano", "h2o", "chainer"]
scientific_comp = ["sympy", "scipy", "sklearn", "numpy", "obspy", "networkx", "cvxpy", "nibabel", "skimage"]
data_visualization = ["matplotlib", "yt", "pyqtgraph"]
programming_tools = ["kubernetes", "lepl", "numba", "IPython"]
# data_analysis = ["pandas"]
# language_processing = ["nltk"]
# object_relation_mapping = ["sqlalchemy"]
# networking = ["twisted"]
# images = ["nibabel", "skimage"]       # NOTE: added to scientific_comp
other = ["pandas", "nltk", "sqlalchemy", "twisted"]

packages = [
    programming_tools,
    scientific_comp,
    data_visualization,
    deep_learning,
    other
]

package_names = [
    "Programming tools",
    "Scientific computing",
    "Data visualization",
    "Deep learning",
    "Other"
]

colors = [
    "#e7298a",
    "#1b9e77",
    "#7570b3",
    "#66a61e",
    "#d95f02",
]

rects = [Rectangle((0, 0), 1, 1, fc=color) for color in colors]


def get_color(mod_name):
    for idx, package_list in enumerate(packages):
        if mod_name in package_list:
            return colors[idx]
    raise ValueError("Mod name {} not found in a mod list".format(mod_name))


code_path = utils.CODE_CORPUS / "corpus" / "code-comment-corpus.pkl"
code_data = pickle.load(open(code_path, "rb"))
paths = [path for (path, line) in code_data.keys()]
modules = list()
for path in paths:
    dot_idx = path.find(".")
    if dot_idx != -1:
        modules.append(path[:dot_idx])
    else:
        modules.append(path)

module_counts = dict()
for mod_name in tqdm(modules, desc="Counting"):
    if mod_name in module_counts:
        module_counts[mod_name] += 1
    else:
        module_counts[mod_name] = 1
# print(module_counts["pickle"])
common_mods = sorted(module_counts.items(), key=lambda tup: tup[0])
print(len(common_mods))
common_mods.sort(key=lambda tup: tup[1], reverse=True)
mods_to_use = common_mods[:25]

(names, amounts) = map(list, zip(*mods_to_use))
indices = list(range(len(names)))
mod_colors = [get_color(name) for name in names]
data = list(zip(names, amounts, mod_colors))

color_to_count = dict()
for name, count, color in data:
    if color not in color_to_count:
        color_to_count[color] = count
    else:
        color_to_count[color] = max((count, color_to_count[color]))

max_counts = [color_to_count[color] for _, _, color in data]
all_data = list(zip(names, amounts, mod_colors, max_counts))

all_data.sort(key=lambda tup: (tup[3], tup[2], tup[1]))
(names, amounts, mod_colors, max_counts) = map(list, zip(*all_data))

plt.figure()
plt.title("Module level corpus contributions")
plt.xlabel("# of usable code/docstring pairs")
plt.ylabel("Module name")
plt.barh(indices, amounts, color=mod_colors)
plt.yticks(indices, names)
plt.legend(rects, package_names)
plt.show()
