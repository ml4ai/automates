def dump_raw_pcode(func, file):
    func_body = func.getBody()
    listing = currentProgram.getListing()
    opiter = listing.getInstructions(func_body, True)
    while opiter.hasNext():
        op = opiter.next()
        raw_pcode = op.getPcode()
        file.write("{}\n".format(op))
        for entry in raw_pcode:
            file.write("  {}\n".format(entry))


file = open(currentProgram.getName() + "-unrefined-PCode.txt", "w")
fm = currentProgram.getFunctionManager()
funcs = fm.getFunctions(True)
for func in funcs:
    dump_raw_pcode(func, file)  # dump straight refined pcode as strings
