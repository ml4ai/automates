## This dir contains exploration of differences between basic math differences between Fortran and Python


### Installing gfortran on mac

I installed homebrew version of gcc, which includes gfortran

`$ brew install gcc`


### Quick "getting started" compiling Fortran on mac

https://stackoverflow.com/questions/37665708/how-to-get-started-with-fortran-on-a-mac

# From terminal:
$ cat >hello.f90 <<EOF
program hello
  implicit none
  write(*,*) 'hello world'
end program hello
EOF

# compile
$ gfortran hello.f90

# execut
$ ./a.out

# If you want to compile to a different named file, use -o :
$ gfortran -o hello hello.f90