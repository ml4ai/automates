packages = list()
with open("../../data/corpus/awesome-python.txt", "r") as infile:
    for i, line in enumerate(infile):
        if "-" in line:
            dirty_name = line[:line.find(" - ")]
            package_name = dirty_name.replace(" ", "_").lower()
            packages.append(package_name)

unique_packages = sorted(list(set(packages)))
with open("requirements-awesome.txt", "w") as outfile:
    outfile.write("\n".join(unique_packages))
