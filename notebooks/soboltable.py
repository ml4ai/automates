import pandas as pd

def table(frames):

    compareS1 = pd.concat(frames, axis=1, sort=False)
    compareS1.fillna('', inplace=True)

    return compareS1


