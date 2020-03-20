      program simulate
      implicit none
      double precision I, beta, gamma, iota, N, delta_t
      double precision L, val1, ifrac

      I = 1.0
      beta = 0.1
      gamma = 0.05
      iota = 0.01
      N = 1000.0
      delta_t = 0.1

      L = beta * (I + iota) / N
      val1 = -L * delta_t
      ifrac = 1.0 - exp(val1)

      write (*,*) beta, gamma, iota, N, delta_t
      write (*,*) L, val1, ifrac

      stop
      end program simulate

