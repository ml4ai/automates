GCCDIR = /usr/local/gcc-10.1.0/bin/

CXX = $(GCCDIR)/g++-10.1
# use CUSTOM_GCC_10_PATH for CXX if it is set
ifdef CUSTOM_GCC_10_PATH
CXX = $(CUSTOM_GCC_10_PATH)
endif
# Flags for the C++ compiler: enable C++11 and all the warnings, -fno-rtti is required for GCC plugins
CXXFLAGS = -std=c++11 -fno-rtti 
# Workaround for an issue of -std=c++11 and the current GCC headers
CXXFLAGS += -Wno-literal-suffix

# Determine the plugin-dir and add it to the flags
PLUGINDIR=$(shell $(CXX) -print-file-name=plugin)
CXXFLAGS += -g -I$(PLUGINDIR)/include -I/usr/local/include

# top level goal: build our plugin as a shared library
#all: mac linux

# IMPORTANT: For Linux machines, use -shared instead of -dynamiclib -undefined dynamic_lookup. For windows machines, there are many more steps.
mac: ast_dump.o
	$(CXX) $(LDFLAGS) -w -dynamiclib -undefined dynamic_lookup -o ast_dump.so $<

linux: 
	$(CXX) $(CXXFLAGS) -w -fPIC -shared -o ast_dump.so ast_dump.cpp

ast_dump.o : ast_dump.cpp
	$(CXX) $(CXXFLAGS) -w -fPIC -c -o $@ $<

clean:
	rm -f ast_dump.o ast_dump.so

check: ast_dump.so
	$(CXX) -fplugin=./ast_dump.so -c -x c++ /dev/null -o /dev/null

.PHONY: all clean check
