from binascii import hexlify
from ghidra.app.util import DisplayableEol

program_name = currentProgram.getName()

file = open(program_name + "-instructions.txt", "w")
file.write('>>> START: DumpInstructions_single_fn.py : {}\n'.format(currentProgram.getName()))

listing = currentProgram.getListing()
main_func = getGlobalFunctions("main")[0]  # assume there's only 1 function named 'main'
addr_set = main_func.getBody()
code_units = listing.getCodeUnits(addr_set, True)  # True means 'forward'

# file.write('inspect: {}'.format(dir(inspect)))
# file.write('Python: {}\n'.format(sys.version_info))
# file.write('DisplayableEol: {}\n'.format(dir(DisplayableEol.__init__)))
# file.write('DisplayableEol.argslist: {}\n'.format(DisplayableEol.__init__.argslist))
# file.write('DisplayableEol.__doc__: {}\n'.format(DisplayableEol.__init__.__doc__))
# DOES NOT WORK file.write('DisplayableEol: {}'.format(DisplayableEol.__init__.__func_code__.co_varnames))
# DOES NOT WORK file.write('DisplayableEol: {}'.format(inspect.signature(DisplayableEol.__init__)))

for code_unit in code_units:
    file.write("0x{} :: {:16} :: {}".format(code_unit.getAddress(),
                                              hexlify(code_unit.getBytes()),
                                              code_unit.toString()))

    deol = DisplayableEol(code_unit, True, True, True, True, 5, True, True)
    if deol.hasAutomatic():
        ac = deol.getAutomaticComment()
        file.write(' >>> {}'.format(ac))

    file.write('\n')

file.write('>>> END: DumpInstructions_single_fn.py : {}\n'.format(currentProgram.getName()))
