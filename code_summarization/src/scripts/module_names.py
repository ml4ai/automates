packages = list()
with open("../../data/corpus/python-module-index.txt", "r") as infile:
    for i, line in enumerate(infile):
        cells = line.split()
        if len(cells) > 0:
            long_name = cells[0]
            # package_name = long_name[:long_name.index(".") - 2]
            packages.append(long_name)

module_imports = sorted(list(set(packages)))
with open("modules.txt", "w") as outfile:
    outfile.write(", ".join(module_imports))
