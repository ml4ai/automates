      subroutine get_growth_rate(doubling_time, growth_rate)
        real doubling_time, growth_rate

        if (doubling_time .eq. 0.0) then
            growth_rate = 0.0
        else
          growth_rate = 2.0 ** (1.0 / doubling_time) - 1.0
        endif
      end subroutine get_growth_rate

      subroutine get_beta(gamma, doubling_time, s_c, relative_contact_rate, beta)
        real growth_rate, s_c, relative_contact_rate, doubling_time
        real inv_contact_rate, updated_growth_rate, gamma, beta

        call get_growth_rate(doubling_time, growth_rate)

        inv_contact_rate = 1.0 - relative_contact_rate
        updated_growth_rate = growth_rate + gamma
        beta = updated_growth_rate / s_c * inv_contact_rate
      end subroutine get_beta


      subroutine sir(s_c, i_c, r_c, doubling_time,
     &               relative_contact_rate, gamma, n)
        real relative_contact_rate, doubling_time
        real s_c, i_c, r_c, n, s_n, i_n, r_n, beta, gamma, scale

        call get_beta(gamma, doubling_time, s_c, relative_contact_rate, beta)

        s_n = (-beta * s_c * i_c) + s_c
        i_n = (beta * s_c * i_c - gamma * i_c) + i_c
        r_n = gamma * i_c + r_c

        scale = n / (s_n + i_n + r_n)

        s_c = s_n * scale
        i_c = i_n * scale
        r_c = r_n * scale
      end subroutine sir
