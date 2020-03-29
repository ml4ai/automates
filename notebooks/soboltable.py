import pandas as pd

def table(frames):

    compareS = pd.concat(frames, sort=False)
    compareS.fillna('', inplace=True)

    return compareS


