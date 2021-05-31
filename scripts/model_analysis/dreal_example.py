from dreal import *

# dreal example from github
x = Variable("x")
y = Variable("y")
z = Variable("z")
f_sat = And(0 <= x, x <= 10,
            0 <= y, y <= 10,
            0 <= z, z <= 10,
            sin(x) + cos(y) == z)
result0 = CheckSatisfiability(f_sat, 0.001)
print(result0)
print()

# dreal example notes
x = Variable("x")
f_sat0 = And(-2 <= x, x <= 2, -x**2 + 0.5*x**4 == 0)
result = CheckSatisfiability(f_sat0, 0.001)
print(result)
print()
f_sat1 = And(-2 <= x, x <= -0.75, -x**2 + 0.5*x**4 == 0)
result1 = CheckSatisfiability(f_sat1, 0.001)
print(result1)
print()
f_sat2 = And(0.75 <= x, x <= 2, -x**2 + 0.5*x**4 == 0)
result2 = CheckSatisfiability(f_sat2, 0.001)
print(result2)
print()


# dreal example 2 notes
x = Variable("x")
y = Variable("y")
f_sat = And(-3 <= x, x <= 3, -3 <= y, y <= 3, (x*y-y)**2 == 0)  # different intervals yield different solutions
result = CheckSatisfiability(f_sat, 0.001)
print(result)


# # dreal with function
# x = Variable("x")
# y = Variable("y")
#
#
# def my_function(x, y):
#     return (x*y-y)**2
#
#
# print()
# print()
# f_sat2= And(-3 <= x, x <= 3, -3 <= y, y <= 3, my_function == 0)
# result = CheckSatisfiability(f_sat2, 0.001)
# print(result)