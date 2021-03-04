## Setting up gcc plugin


### Requirements

* gmp libraries
    * On mac `brew install gmp`
    * On linux install `libgmp3-dev` with configured package manager
* On mac, command line developer tools are required
  * Use `xcode-select --install`

### Building GCC on linux

TODO 

### Building GCC on macos

Taken from: https://solarianprogrammer.com/2019/10/12/compiling-gcc-macos/. The instructions below were written using gcc 10.1.0.

1) Move into the gcc-plugin directory in the automates repository.
2) Create a directory to download the gcc files into: `mkdir gcc_all & cd gcc_all`
3) Download gcc tarball and extract into the folder `curl -L https://ftpmirror.gnu.org/gcc/gcc-10.1.0/gcc-10.1.0.tar.xz | tar xf -`
4) Download gcc preqrequesites via provided script `cd gcc-10.1.0 & contrib/download_prerequisites`
5) Now configure and build the compiler (this will take awhile (~1hr) and take up a good amount of space (~4gb)). From `/gcc_all/gcc-10.1.0`, run

`mkdir build && cd build`
`../configure --prefix=/usr/local/gcc-10.1.0 --enable-plugin --enable-checking=release --enable-languages=c,c++,fortran --with-sysroot=/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk --program-suffix=-10.1`
`make -j$(getconf _NPROCESSORS_ONLN)`

Note that the configure specifies we are enabling gcc for c, c++, and fortran. This will allow us to install gcc, g++, and g-fortran.

1) Install the gcc-10 binarys into your bin: `sudo make install`
2) Test if it works with an example c file: `/usr/local/gcc-10.1.0/bin/g++-10.1 example.c`

### Building Plugin

You can use the makefile found in the `./plugins` directory to build the plugin. The plugin source code is found in `./plugins/ast_dump.cpp`. Running `make` will compile the plugin to a `.so` (shared object) file. This shared object file can then be referenced in future compilation commands to run the plugin. To test that the plugin compiled successfully, run `make check`. If there is no outputs/errors, it compiled successfully!

### Executing Plugin

To run the plugin on a particuler c/c++ file, run the following and replace `example.c` with your file:

`/usr/local/gcc-10.1.0/bin/g++-10.1 -fplugin=./ast_dump.so -c -x c++ example.c -o /dev/null`

To run the plugin on a particuler fortran file, run the following and replace `example.f` with your file:

`/usr/local/gcc-10.1.0/bin/gfortran-10.1 -fplugin=./ast_dump.so -c example.f -o /dev/null`
