      subroutine sir()
        implicit none
        s_n = (-beta * s * i) + s
        i_n = (beta * s * i - gamma * i) + i
        r_n = gamma * i + r
        scale = n / (s_n + i_n + r_n)

        s_n * scale, i_n * scale, r_n * scale
      end subroutine sir


      program main

        implicit none


      end program main
