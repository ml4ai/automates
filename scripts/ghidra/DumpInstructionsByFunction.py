from binascii import hexlify
from ghidra.app.util import DisplayableEol

PROGRAM_NAME = currentProgram.getName()

FILE = open(PROGRAM_NAME + "-instructions.txt", "w")
FILE.write('>>> FILE_START: {}\n'.format(currentProgram.getName()))

LISTING = currentProgram.getListing()
FM = currentProgram.getFunctionManager()
FUNCTIONS = FM.getFunctions(True)  # True means 'forward'


def write_instructions(code_units):
    for code_unit in code_units:
        FILE.write("0x{} :: {}"  # "0x{} :: {:16} :: {}"
                   .format(code_unit.getAddress(),
                   # hexlify(code_unit.getBytes()),
                   code_unit.toString()))

        deol = DisplayableEol(code_unit, True, True, True, True, 5, True, True)
        if deol.hasAutomatic():
            ac = deol.getAutomaticComment()
            FILE.write(' >>> {}'.format(ac))

        FILE.write('\n')


# main_func = getGlobalFunctions("main")[0]  # assume there's only 1 function named 'main'
# addr_set = main_func.getBody()
# code_units = LISTING.getCodeUnits(addr_set, True)  # True means 'forward'


for fn in FUNCTIONS:
    fn_name = fn.getName()
    fn_entry_point = fn.getEntryPoint()
    FILE.write(">>> FUNCTION_START: {} {}\n".format(fn_entry_point, fn_name))

    addr_set = fn.getBody()
    # FILE.write("type(addr_set): {}\n".format(type(addr_set)))

    # FILE.write("addr_set: {}\n".format(addr_set))
    # addr_set_first_range = addr_set.getFirstRange()
    # FILE.write("addr_set_first: {}\n".format(addr_set_first_range))
    # FILE.write("type(addr_set_first): {}\n".format(type(addr_set_first_range)))
    # addr_set_last_range = addr_set.getLastRange()
    # FILE.write("addr_set_last: {}\n".format(addr_set_last_range))
    # FILE.write("type(addr_set_last): {}\n".format(type(addr_set_last_range)))
    # FILE.write("type(addr_set) {}:\n".format(type(addr_set)))
    # FILE.write("dir(addr_set) {}:\n".format(dir(addr_set)))

    addr_set_min = addr_set.getMinAddress()
    addr_set_max = addr_set.getMaxAddress()
    FILE.write("addr_set_min: {}\n".format(addr_set_min))
    FILE.write("addr_set_max: {}\n".format(addr_set_max))
    # FILE.write("type(addr_set_min): {}\n".format(type(addr_set_min)))  # ghidra.program.model.address.GenericAddress
    # FILE.write("dir(addr_set_min): {}\n".format(dir(addr_set_min)))
    # addr_set_min_addr = addr_set_min.getAddress()  # Does not work: getAddress requires an argument

    # FILE.write("type(fn_entry_point): {}\n".format(type(fn_entry_point)))
    # FILE.write("dir(fn_entry_point): {}\n".format(dir(fn_entry_point)))

    code_units = LISTING.getCodeUnits(addr_set, True)
    write_instructions(code_units)
    FILE.write(">>> FUNCTION_END: {} {}\n".format(fn_entry_point, fn_name))


# file.write("\ntype(main_func):  {}\n".format(type(main_func)))
# file.write("dir(main_func):   {}\n".format(dir(main_func)))
#
# file.write("\ntype(code_units): {}\n".format(type(code_units)))
# file.write("dir(code_units):  {}\n".format(dir(code_units)))

FILE.write('>>> FILE_END: {}\n'.format(currentProgram.getName()))
