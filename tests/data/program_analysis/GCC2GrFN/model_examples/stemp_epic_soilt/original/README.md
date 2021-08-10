Configuring the build

It is usually preferred that you do an out-of-source build. To do this, create a build/ directory at the top level of your project and build there.

$ mkdir build
$ cd build
$ cmake ..
$ make

When you do this, temporary CMake files will not be created in your src/ directory.