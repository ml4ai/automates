## Model Analysis
The MA team has been working closely with the PA team since our last report to update the creation and handling of GrFNs to support the AutoMATES collaboration with the GTRI and Galois teams for our joint demo. The members of the collaboration have all chosen to work with the `SIR` model family of infectious diseases. The majority of the updates in this report are extensions and revisions to the creation of GrFN computation graphs for the `SIR` model family. In addition we also present a new translation service, `GrFN2WD`, which handles the translation of GrFNs in `WiringDiagrams`, a construct used by the `GTRI` team to represent knowledge graphs in `SemanticModels.jl`.

<!--
TODO Souratosh (S), Paul (P) -  Updates on the following:
* S: Current status of dReal and Ibex experimentation and interval contraction approach
* S: other updates?
-->

#### Updates to GrFN Wiring and Execution
In this section of the report we introduce updates to the GrFN CG generation and execution that are necessary to support the Gillespie SIR model (provided to the AutoMATES team by the Galois team). The GrFN CG view of this model is shown below.
![Gillespie SIR Model GrFN](figs/SIR-gillespie_alt.png)

###### Generalizing Loop Semantics and Execution
- Allows us to handle `break`, `continue`, and nested `return`
- Nested loop execution semantics with subgraphs
![Loop Exit Example](figs/EXIT-example.png)

###### Introducing the Container Uniqueness Index
![GrFN Container Multi-call Example](figs/multi-call-example.png)

###### Transformation to model/solver representation
![Gillespie SIR GrFN CAG Model/Solver Separation](figs/SIR-gillespie-CAG_alt.png)

#### Translating GrFN to WiringDiagrams for SemanticModels.jl
```Fortran
subroutine sir(S, I, R, beta, gamma, dt)
  implicit none
  double precision S, I, R, beta, gamma, dt
  double precision infected, recovered

  infected = (-(beta*S*I) / (S + I + R)) * dt
  recovered = (gamma*I) * dt

  S = S - infected
  I = I + infected - recovered
  R = R + recovered
end subroutine sir
```

![Simplified SIR Model GrFN](figs/SIR-simple--GrFN.png)

```julia
using Catlab
using Catlab.WiringDiagrams
using Catlab.Doctrines
import Catlab.Doctrines: ⊗, id
import Base: ∘
include("SIR-simple__functions.jl")
⊗(a::WiringDiagram, b::WiringDiagram) = otimes(a, b)
∘(a::WiringDiagram, b::WiringDiagram) = compose(b, a)
⊚(a,b) = b ∘ a

beta_0, S_0, I_0, R_0, dt_0, gamma_0 = Ob(FreeSymmetricMonoidalCategory, :beta_0, :S_0, :I_0, :R_0, :dt_0, :gamma_0)
recovered_1, infected_1 = Ob(FreeSymmetricMonoidalCategory, :recovered_1, :infected_1)
S_1, R_1, I_1 = Ob(FreeSymmetricMonoidalCategory, :S_1, :R_1, :I_1)

id_I_0 = id(Ports([I_0]))
id_R_0 = id(Ports([R_0]))
id_S_0 = id(Ports([S_0]))

IN_1 = WiringDiagram(Hom(:L0_REWIRE, beta_0 ⊗ S_0 ⊗ I_0 ⊗ R_0 ⊗ dt_0 ⊗ gamma_0, gamma_0 ⊗ I_0 ⊗ dt_0 ⊗ beta_0 ⊗ S_0 ⊗ I_0 ⊗ R_0 ⊗ dt_0 ⊗ I_0 ⊗ R_0 ⊗ S_0))
WD_infected_1 = WiringDiagram(Hom(A__infected_1, beta_0 ⊗ S_0 ⊗ I_0 ⊗ R_0 ⊗ dt_0, infected_1))
WD_recovered_1 = WiringDiagram(Hom(A__recovered_1, gamma_0 ⊗ I_0 ⊗ dt_0, recovered_1))
OUT_1 = IN_1 ⊚ (WD_recovered_1 ⊗ WD_infected_1 ⊗ id_I_0 ⊗ id_R_0 ⊗ id_S_0)

IN_1 = WiringDiagram(Hom(:L1_REWIRE, recovered_1 ⊗ infected_1 ⊗ I_0 ⊗ R_0 ⊗ S_0, S_0 ⊗ infected_1 ⊗ R_0 ⊗ recovered_1 ⊗ I_0 ⊗ infected_1 ⊗ recovered_1))
WD_I_1 = WiringDiagram(Hom(A__I_1, I_0 ⊗ infected_1 ⊗ recovered_1, I_1))
WD_R_1 = WiringDiagram(Hom(A__R_1, R_0 ⊗ recovered_1, R_1))
WD_S_1 = WiringDiagram(Hom(A__S_1, S_0 ⊗ infected_1, S_1))
OUT_2 = OUT_1 ⊚ IN_1 ⊚ (WD_S_1 ⊗ WD_R_1 ⊗ WD_I_1)
```
![Simplified SIR Model WiringDiagram](figs/translated-WD.png)

#### Domain Constraint Propagation
The task of domain constraint propagation, introduced in previous reports, has been placed on hold while we work on completing the necessary components of the AutoMATES pipeline to facilitate our collaboration with the GTRI and Galois teams.
