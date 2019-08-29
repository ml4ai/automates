## Program Analysis

In prior reporting periods, program analysis had focused on front end processing: lifting Fortran source code into a Python-based intermediate representation (IR) and translating a subset of the associated language features into the GrFN representation used for downstream analyses.  During the current reporting period, program analysis efforts focused on two objectives: (1) extending the translation to GrFN to encompass a wider variety of Fortran source-language features; and (2) applying and evaluating our tools on software for the SIR model for infectious diseases.  The extensions to GrFN involved formalizing the handling of loops and arrays and extending the GrFN generator to implement the translation to the extended GrFN representation.  Applying our tools to infectious disease models helped showcase the robustness of our tools as well as identify areas for improvement.

### Array

* In SIR model, arrays are used as containers to store the computed means and variances of susceptible, infected, and recovered population from the disease. Thus, for this reporting period, implementing GrFN for arrays has been one of the main focuses, so the SIR model can be translated from Fortran to Python to GrFN.
* The structure (i.e. name, scope function, dimension, and data type, etc) of an array is represented in JSON while actual data values are retrieved via lambda functions.
* Arrays require accessors to get and set the data values. Depending on which accessor is needed -- which can be extracted from the Python IR -- we generate lambda functions in the GrFN to access the data appropriately. For example,
    * Fortran: means(k) = means(k) + (n - means(k))/(runs+1)
    * Python: means.set_((k[0]), (means.get_((k[0])) + ((n[0] - means.get_((k[0]))) / (runs[0] + 1))))
    * GrFN lambda:
        ```
        def arrays_basic__main__assign__means_k__0(means, n: real, runs: int):
            means[k] = (means[k]+((n-means[k])/(runs+1)))
	        return means[k]
	    ```

### Loops

* As we started handling more complex models with higher code complexity, a more comprehensive GrFN schema was required. In this context, the representation of loops in GrFN changed significantly.
* Moving from loops being represented as `loop_plates` in the old GrFN schema, we represent them as `containers`, similar to how functions are represented in the new GrFN schema. Hence, loops are viewed as a block having `arguments`, `outputs` and a `body`.
	* The core difference between a `function` container and a `loop` container is that a `loop` container executes                 indefinitely until an `EXIT` criterion is met.
	* The `argument` to a loop container is all variables that are used as inputs inside the loop body.
	* Any loop `argument` that is updated inside the loop body will appear in the `updated` field of the container.
	* The `body` of a loop container now contains functions that check for the `EXIT` conditions of the loop. With the 	     help of `IF` condition functions to check for the loop conditionals and `EXIT` decision functions to decide whether           or not a loop should break its flow, loops can now be represented as repeating containers.
* A loop will also appear as a function inside another container. Here, it will have `inputs` and `updates`. The name of this function will be the same as that of its container.
* In addition to incorporating the above mentioned schema changes for `for` loops, complete handling of `while` loops was achieved for this reporting period as well, the structure of which closes follows that of the `for` loop. 
