
# Preprocessing :

# label nodes <-> Index of left1/left2 and keyroots1/keyroots2 arrays
position = [0,  1, 2,  3, 4, 5, 6]

# Left most descendants of each tree
left1 = [None, 1, 1, 3, 4, 1, 1]
left2 = [None, 1, 1, 3, 3, 5, 1]

# keyroots are functions that take the trees as inputs and generate the keyroots 
keyroots1  = [None, 0, 0, 1, 1, 0, 1]
keyroots2 = [None, 0, 0, 0, 1, 1, 1]

def compute(t1 : tree, t2: tree):

    for s in range(0, len(keyroots1)):
        for t in range(0, len(keyroots2)):
            i = keyroots1[s]
            j = keyroots2[t]

            _, tdist = treedist(i, j)

    return tdist[i][j]

def treedist(pos1, pos2):
    bound1 = pos1 - left1[pos1] + 2
    bound2 = pos2 - left2[pos2] + 2

    fdist =  [[None for i in range(0, bound1)] for j in range(0, bound2)]

    fdist[0][0] =  0
    for i in range(0, bound1):
        fdist[i][0] = fdist[i-1][0] + c[1][0]
    for i in range(0, bound1):
        fdist[0][i] = fdist[0][i-1] + c[0][1]

    for k in range(left1[pos1], pos1, -1):
        for i in range(1, k):
            for l in range(left2[pos2], pos2, -1):
                for j in range(0, l):
            if left1[k] == left1[pos1] and left2[l] == left2[pos2]:
                fdist[i][j] = min(fdist[i-1][j] + c[0][l], fdist[i][j-1] +\
                        c[k][0], fdist[i-1][j-1] + c[k][l])

                tdist[k][l] = fdist[i][j]
            else:
                m = left1[k] - left1[pos1]
                n = left2[l] - left2[pos2]
                fdist[i][j] = min(fdist[i-1][j] + c[0][l], fdist[i][j-1] +\
                        c[k][0], fdist[i-1][j-1] +  tdist[k][l])


    return fdist, tdist

print()
