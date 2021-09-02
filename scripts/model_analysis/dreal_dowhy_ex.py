from dreal import *
import dowhy as dw

# dreal example from github
x = Variable("x")
y = Variable("y")
z = Variable("z")
f_sat = And(0 <= x, x <= 10,
            0 <= y, y <= 10,
            0 <= z, z <= 10,
            sin(x) + cos(y) == z)
result0 = CheckSatisfiability(f_sat, 0.001)
# print(result0)
# print()

# dreal example notes
x = Variable("x")
f_sat0 = And(-2 <= x, x <= 2, -x**2 + 0.5*x**4 == 0)
result = CheckSatisfiability(f_sat0, 0.001)
# print(result)
# print()
f_sat1 = And(-2 <= x, x <= -0.75, -x**2 + 0.5*x**4 == 0)
result1 = CheckSatisfiability(f_sat1, 0.001)
# print(result1)
# print()
f_sat2 = And(0.75 <= x, x <= 2, -x**2 + 0.5*x**4 == 0)
result2 = CheckSatisfiability(f_sat2, 0.001)
# print(result2)
# print()


# dreal example 2 notes
x = Variable("x")
y = Variable("y")
f_sat = And(-3 <= x, x <= 3, -3 <= y, y <= 3, (x*y-y)**2 == 0)  # different intervals yield different solutions
result = CheckSatisfiability(f_sat, 0.001)
# print(result)

# DoWhy Examples
dot_graph = 'digraph {; U1 [latent,pos="-0.513,-1.276"]; U2 [latent,pos="-1.614,-0.275"]; \
U3 [latent,pos="-1.140,-0.373"]; U4 [latent,pos="0.120,-0.355"]; W1 [pos="-1.134,-0.724"]; \
W2 [pos="-0.840,0.007"]; X [exposure,pos="-0.480,-0.724"]; Y1 [outcome,pos="0.194,-0.724"]; \
Y2 [outcome,pos="-0.153,0.007"]; U1 -> W1; U1 -> Y1; U2 -> W1; U2 -> W2; U3 -> W2; U3 -> X; \
U4 -> X; U4 -> Y2; W1 -> X; W2 -> Y2; X -> Y1;}'

# model = dw.CausalModel(data=None, treatment="X", outcome=["Y1", "Y2"], graph=dot_graph)