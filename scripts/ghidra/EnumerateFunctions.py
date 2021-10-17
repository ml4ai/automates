program_name = currentProgram.getName()
file = open(program_name + "-functions.txt", "w")

fm = currentProgram.getFunctionManager()
funcs = fm.getFunctions(True)  # True means 'forward'
for func in funcs:
    file.write("Function: {} @ 0x{}\n".format(func.getName(), func.getEntryPoint()))
