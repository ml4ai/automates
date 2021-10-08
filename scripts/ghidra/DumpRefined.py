from ghidra.util.task import ConsoleTaskMonitor
from ghidra.app.decompiler import DecompileOptions, DecompInterface

# == helper functions =============================================================================
def get_high_function(func):
    options = DecompileOptions()
    monitor = ConsoleTaskMonitor()
    ifc = DecompInterface()
    ifc.setOptions(options)
    ifc.openProgram(getCurrentProgram())
    # Setting a simplification style will strip useful `indirect` information.
    # Please don't use this unless you know awhy you're using it.
    # ifc.setSimplificationStyle("normalize")
    res = ifc.decompileFunction(func, 60, monitor)
    high = res.getHighFunction()
    return high


def dump_refined_pcode(func, high_func, file):
    opiter = high_func.getPcodeOps()
    while opiter.hasNext():
        op = opiter.next()
        file.write("{}\n".format(op.toString()))


# == run examples =================================================================================

file = open(currentProgram.getName() + "-refined-PCode.txt", "w")
fm = currentProgram.getFunctionManager()
funcs = fm.getFunctions(True)
for func in funcs:
    hf = get_high_function(func)  # we need a high function from the decompiler
    dump_refined_pcode(func, hf, file)  # dump straight refined pcode as strings
