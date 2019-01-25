reqs = list()
# with open("pipreqs.txt", "r") as infile:
#     for line in infile:
#         cells = line.split()
#         reqs.append(cells[0])
#
#
# with open("requirements-full.txt", "w") as outfile:
#     outfile.write("\n".join(reqs))
with open("modules-full.txt", "r") as infile:
    for line in infile:
        # line.replace("-", "_").rstrip()
        reqs.append(line.replace("-", "_").rstrip().lower())
print(reqs)

with open("modules-full-clean-2.txt", "w") as outfile:
    outfile.write(", ".join(reqs))
