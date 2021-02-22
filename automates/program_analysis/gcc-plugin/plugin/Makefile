GCCDIR = /usr/local/gcc-10.1.0/bin/

CXX = $(GCCDIR)/g++-10.1
# Flags for the C++ compiler: enable C++11 and all the warnings, -fno-rtti is required for GCC plugins
CXXFLAGS = -std=c++11 -fno-rtti 
# Workaround for an issue of -std=c++11 and the current GCC headers
CXXFLAGS += -Wno-literal-suffix

# Determine the plugin-dir and add it to the flags
PLUGINDIR=$(shell $(CXX) -print-file-name=plugin)
CXXFLAGS += -g -I$(PLUGINDIR)/include -I/usr/local/include

# top level goal: build our plugin as a shared library
all: ast_dump.so

# IMPORTANT: For Linux machines, use -shared instead of -dynamiclib -undefined dynamic_lookup. For windows machines, there are many more steps.
ast_dump.so: ast_dump.o
	$(CXX) $(LDFLAGS) -w -dynamiclib -undefined dynamic_lookup -o $@ $<

ast_dump.o : ast_dump.cpp
	$(CXX) $(CXXFLAGS) -w -fPIC -c -o $@ $<

clean:
	rm -f ast_dump.o ast_dump.so

check: ast_dump.so
	$(CXX) -fplugin=./ast_dump.so -c -x c++ /dev/null -o /dev/null

.PHONY: all clean check
