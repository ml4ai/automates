# This Ghidra Plugin iterates through Ghidra-identified functions
# and for each it extracts and writes the instructions.
# also handles globals

from ghidra.app.util import DisplayableEol
import ghidra.program.model.symbol.SymbolType as symbolType

# list of address for global variables
address_globbal_variables = []
symbolManager = currentProgram.getSymbolTable()
namespaceManager = currentProgram.getNamespaceManager()
symbols = symbolManager.getSymbols(namespaceManager.getGlobalNamespace())

for symbol in symbols:
    if symbol.getSymbolType() == symbolType.LABEL:
        address_globbal_variables.append('0x' + str(symbol.getAddress()))

PROGRAM_NAME = currentProgram.getName()

with open(PROGRAM_NAME + "-instructions.txt", "w") as write_file:
    write_file.write('>>> FILE_START: {}\n'.format(currentProgram.getName()))
    write_file.write('>>> GLOBALS: {}\n'.format(str(address_globbal_variables)))

    LISTING = currentProgram.getListing()
    FM = currentProgram.getFunctionManager()
    FUNCTIONS = FM.getFunctions(True)  # True means 'forward'


    def write_instructions(code_units):
        for code_unit in code_units:
            write_file.write("0x{} :: {}"  # "0x{} :: {:16} :: {}"
                             .format(code_unit.getAddress(),
                                     # hexlify(code_unit.getBytes()),
                                     code_unit.toString()))

            deol = DisplayableEol(code_unit, True, True, True, True, 5, True, True)
            if deol.hasAutomatic():
                ac = deol.getAutomaticComment()
                # all_comments = deol.getComments()  # does not appear to be different from getAutomaticComments() ?
                # FILE.write(' >>> {} >>> {}'.format(ac, all_comments))
                write_file.write(' >>> {}'.format(ac))

            write_file.write('\n')


    for fn in FUNCTIONS:
        fn_name = fn.getName()
        fn_entry_point = fn.getEntryPoint()
        write_file.write(">>> FUNCTION_START: {} {}\n".format(fn_entry_point, fn_name))

        addr_set = fn.getBody()
        addr_set_min = addr_set.getMinAddress()
        addr_set_max = addr_set.getMaxAddress()
        write_file.write("addr_set_min: {}\n".format(addr_set_min))
        write_file.write("addr_set_max: {}\n".format(addr_set_max))

        code_units = LISTING.getCodeUnits(addr_set, True)
        write_instructions(code_units)
        write_file.write(">>> FUNCTION_END: {} {}\n".format(fn_entry_point, fn_name))

    write_file.write('>>> FILE_END: {}\n'.format(currentProgram.getName()))
