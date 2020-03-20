## Model Analysis

### Variable Domain Constraint Propagation
During phase 1 the model analysis team identified instances of input sets to the PETASCE Evapo-transpiration model that caused bound errors during evaluation. This is due to the bound constraints of certain mathematical functions used in PETASCE, such as `arccos` and `log`. These constraints can be buried deep within the model architecture and commonly place shared constraints on more than one variable value. Some examples of constraints found in the PETASCE model are shared below.

```Fortran
RHMIN = MAX(20.0, MIN(80.0, EA/EMAX*100.0))   ! EMAX must not be 0
RNL = 4.901E-9*FCD*(0.34-0.14*SQRT(EA))*TK4   ! EA must be non-negative

! The inner expression is bounded by [-1, 1] and this bound propagates to
! expression of three variables.
WS = ACOS(-1.0*TAN(XLAT*PIE/180.0)*TAN(LDELTA))
```

Automating the process of sensitivity analysis for any input set will require static analysis to determine the set of domain constraints that can be used to validate an input. Then when running a model the first step will be to validate the input set to ensure that the inputs fit within the domains. For sensitivity analysis that includes a sampling step over a set of bounds this will require validation of the runtime bounds and possibly amending the sampling process for different sensitivity methods to ensure that samples are not taken from areas out of the constrained domain. Currently the MA team is working on a method to determine the bounds for a model by doing a forward/backward pass of bounds over the model, starting with calculating the range value interval constraints of variables in a forward pass and then using this information to calculate the variable domain value interval constraints of variables during the backward pass.

### Senstivity Analysis of PETPT (Priestley-Taylor) model

Model analysis currently uses the computation of Sobol indices to measure the variance in the output as a
function of the fluctuations in the input parameters. 

The AutoMATES MA pipeline current uses the [SALib](https://salib.readthedocs.io/en/latest/) python library, which provides functionality for three
different sensitivity methods, Sobol, Fourier Amplitude Sensitivity Test (FAST), and Random Balance Design-Fourier Amplitude Sensitivity Test (RBD-FAST). This phase we explored using these models for sensitivity analysis. We compared the first order indices ($$S_i$$; $$i$$ is the variable) across the PETPT and ASCE models.

(The Priestley-Taylor (PETPT) model is an example of an
evapotranspiration (EO) model where the daily EO rate of a crop depends on the following independent
variables - the maximum (TMAX) and minimum (TMIN) observable temperatures within a
given day, daily solar radiation (SRAD), leaf area index (XHLAI), and soil
albedo coefficient (MSALB).)

Our results indicate that for reasonable approximations of the input parameter
bounds, $$S_i$$ values are maximum for TMAX and minimum (zero) for
XHLAI in all three methods. SRAD followed by MSALB have the most significant
$$S_i$$'s after TMAX while the sobol index for TMIN in the PETPT model is
negligible. The Sobol method can compute the second order index ($$S_{ij}$$; for
the variables $$i$$ and $$j$$) as
well. Interestingly, we find that while $$S_{XHLAI}$$ is vanishingly small,
the second order index of XHLAI and TMAX is significantly large. Again,
$$S_{ij}$$ for $$(i, j)=$$ (TMAX, SRAD) is non-negligible. In addition, the runtime for each of
the sensitivity analysis methods is computed and compared for different sample
sizes. It becomes evident that for large sample sizes ($$\sim 10^6$), Sobol is
two orders of magnitude slower than both FAST and RBD-FAST methods. In summary,
TMAX is the most significant parameter and any significant change in its value will
have the maximum effect on the EO rate. Our future goal is to extend our
discussion of sensitivity analysis to the PETASCE model in which the EO rate
depends on the
independent variables discussed above as well as a new set of input parameters.
