# Collect all functions by entry-point
# Then walks functions, identifying their calls

program_name = currentProgram.getName()
file = open(program_name + "-functions.txt", "w")

fm = currentProgram.getFunctionManager()
funcs = fm.getFunctions(True)  # True means 'forward'

function_by_entrypoint = dict()

for func in funcs:
    function_by_entrypoint[func.getEntryPoint()] = func.getName()

for entry_point, fn_name in function_by_entrypoint.iteritems():
    file.write("Function: 0x{} --> {}\n".format(entry_point, fn_name))
    references = getReferencesTo(entry_point)
    for xref in references:
        file.write("  {}\n".format(xref))
        from_address = xref.getFromAddress()
        if from_address in function_by_entrypoint:
            file.write("    >>> From Function: {}".format(function_by_entrypoint[from_address]))
        file.write("    getFromAddress:   {}\n".format(xref.getFromAddress()))
        file.write("    getToAddress:     {}\n".format(xref.getToAddress()))
        file.write("    getReferenceType: {}\n".format(xref.getReferenceType()))
        file.write("    getOperandIndex:  {}\n".format(xref.getOperandIndex()))
        file.write("    getSource:        {}\n".format(xref.getSource()))
        file.write("    getSymbolID:      {}\n".format(xref.getSymbolID()))
        file.write("    getClass:         {}\n".format(xref.getClass()))
        file.write("    externalReference {}\n".format(xref.externalReference))
        file.write("    memoryReference   {}\n".format(xref.memoryReference))
        file.write("    MNEMONIC          {}\n".format(xref.MNEMONIC))

        # file.write("  {}\n".format(type(xref)))
        # file.write("  {}\n".format(dir(xref)))
