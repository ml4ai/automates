## Program Analysis

In prior reporting periods, program analysis had focused on front end processing: lifting Fortran source code into a Python-based intermediate representation (IR) and translating a subset of the associated language features into the GrFN representation used for downstream analyses.  During the current reporting period, program analysis efforts focused on two objectives: (1) extending the translation to GrFN to encompass a wider variety of Fortran source-language features; and (2) applying and evaluating our tools on software for the SIR model for infectious diseases.  The extensions to GrFN involved formalizing the handling of loops and arrays and extending the GrFN generator to implement the translation to the extended GrFN representation.  Applying our tools to infectious disease models helped showcase the robustness of our tools as well as identify areas for improvement.

### Array

* In SIR model, arrays are used as containers to store the computed means and variances of susceptible, infected, and recovered population from the disease. Thus, for this reporting period, implementing GrFN for arrays has been one of the main focuses, so the SIR model can be translated from Fortran to Python to GrFN.
* The structure (i.e. name, scope function, dimension, and data type, etc) of an array is represented in JSON while actual data values are retrieved via lambda functions.
* Arrays require accessors to set (setter) and get (getter) the data values. Depends on which accessor is needed (this can be extracted from the Python IR), GrFN generators (genPGM and genCode) generates relevant lambda functions to set and/or get the data. For example,
    * Fortran: means(k) = means(k) + (n - means(k))/(runs+1)
    * Python: means.set_((k[0]), (means.get_((k[0])) + ((n[0] - means.get_((k[0]))) / (runs[0] + 1))))
    * GrFN lambda:
        ```
        def arrays_basic__main__assign__means_k__0(means, n: real, runs: int):
            means[k] = (means[k]+((n-means[k])/(runs+1)))
	        return means[k]
	    ```
