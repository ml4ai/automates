GCCDIR = /bin
CXX = $(GCCDIR)/g++-9
FORTRAN_COMPILER = $(GCCDIR)/gfortran-9

# Flags for the C++ compiler: enable C++11 and all the warnings, -fno-rtti is required for GCC plugins
CXXFLAGS = -std=c++11 -Wall -fno-rtti 
# Workaround for an issue of -std=c++11 and the current GCC headers
#CXXFLAGS += -Wno-literal-suffix

# Determine the plugin-dir and add it to the flags
PLUGINDIR=$(shell $(CXX) -print-file-name=plugin)
CXXFLAGS += -g -I$(PLUGINDIR)/include -I/gcc-9.3.0/gcc/ -I/usr/lib/gcc/x86_64-pc-linux-gnu/9.3.0/plugin/include/

# top level goal: build our plugin as a shared library
all: ast_plugin.so

# For Linux machines, use -shared instead of -dynamiclib -undefined dynamic_lookup. For windows machines, there are many more steps.
ast_plugin.so: ast_plugin.o
	$(CXX) $(LDFLAGS) -w -shared -o $@ $<

ast_plugin.o: ast_plugin.cpp
	$(CXX) $(CXXFLAGS) -w -fPIC -c -o $@ $<

clean:
	rm -f ast_plugin.o ast_plugin.so

#/bin/g++-9 -std=c++11 -Wall -fno-rtti  -g -I/usr/lib/gcc/x86_64-linux-gnu/9/plugin/include -I/gcc-9.3.0/gcc/ -I/usr/lib/gcc/x86_64-pc-linux-gnu/9.3.0/plugin/include/ -w -fPIC -c -o ast_plugin.o ast_plugin.cpp

.PHONY: all clean check