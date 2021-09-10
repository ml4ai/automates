import dreal as dr
import dowhy as dw
import pandas as pd
import dowhy.datasets

# dreal example from github
x = dr.Variable("x")
y = dr.Variable("y")
z = dr.Variable("z")
f_sat = dr.And(0 <= x, x <= 10,
               0 <= y, y <= 10,
               0 <= z, z <= 10,
               dr.sin(x) + dr.cos(y) == z)
result0 = dr.CheckSatisfiability(f_sat, 0.001)
# print(result0)
# print()

# dreal example notes
x = dr.Variable("x")
f_sat0 = dr.And(-2 <= x, x <= 2, -x**2 + 0.5*x**4 == 0)
result = dr.CheckSatisfiability(f_sat0, 0.001)
# print(result)
# print()
f_sat1 = dr.And(-2 <= x, x <= -0.75, -x**2 + 0.5*x**4 == 0)
result1 = dr.CheckSatisfiability(f_sat1, 0.001)
# print(result1)
# print()
f_sat2 = dr.And(0.75 <= x, x <= 2, -x**2 + 0.5*x**4 == 0)
result2 = dr.CheckSatisfiability(f_sat2, 0.001)
# print(result2)
# print()


# dreal example 2 notes
x = dr.Variable("x")
y = dr.Variable("y")
f_sat = dr.And(-3 <= x, x <= 3, -3 <= y, y <= 3, (x*y-y)**2 == 0)  # different intervals yield different solutions
result = dr.CheckSatisfiability(f_sat, 0.001)
# print(result)

# DoWhy Examples
dot_graph = 'digraph { U1 [latent,pos="-0.513,-1.276"]; U2 [latent,pos="-1.614,-0.275"]; U3 [latent,pos="-0.850,-0.392"]; U4 [latent,pos="0.120,-0.355"]; W1 [pos="-1.134,-0.724"]; W2 [pos="-0.840,0.007"]; X [pos="-0.480,-0.724"]; Y1 [pos="0.194,-0.724"]; Y2 [pos="-0.153,0.007"]; U1 -> W1; U1 -> Y1; U2 -> W1; U2 -> W2; U3 -> W2; U3 -> X; U4 -> W1; U4 -> Y2; W1 -> X; W2 -> Y2; X -> Y1}'

# I construct a dataframe with arbitrarily chosen observations
data = [[0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1],
        [2, 2, 2, 2, 2],
        [0, 0, 0, 0, 0],
        [1, 2, 3, 4, 5]]
df = pd.DataFrame(data, columns=["X", "W1", "W2", "Y1", "Y2"])
model = dw.CausalModel(data=df, treatment=["X"], outcome=["Y1", "Y2"], graph=dot_graph)
identification = model.identify_effect(estimand_type="nonparametric-ate", method_name="default",
                                       proceed_when_unidentifiable=True)
print(identification)



# model = dw.CausalModel(data=None, treatment="X", outcome=["Y1", "Y2"], graph=dot_graph)