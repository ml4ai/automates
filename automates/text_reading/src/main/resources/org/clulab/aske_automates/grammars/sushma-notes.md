### Notes for Population count Rules

#### Problem definition
Events that indicate the number of people in an experiment and have two arguments ("population" and "number").

1) Input source: <a href="https://www.pnas.org/doi/pdf/10.1073/pnas.2111091119">example input</a>
2) Here the examples of populations are as follows:
    - _preregistered experiment (n = 25,718 from 89 countries) tested hypotheses_
    - mentions of Population keyword without any numbers: 4
    - Rule for number of people in the experiment as **"(n= )"** rule.
3) Some indirect examples since there are examples such as N = 23,554 :
    - _B is the unstandardized coefficient; rp is the partial standardized effect size for each coefficient. N = 23,554. Controlling: n = 7,688; no message: n = 8,059; autonomy supportive: n = 7,807_
    **Notes** For this example, N is a population size of an experiment in Statistics. 
    n is a Sample size of an experiment.
    - Where as in this input document, examples do seem to refer to population sizes and samples sizes - each of which could be possible candidates for population samples entities.
    - This could be two additional rules: "N =" and "n =" which are closer to the tables.
4) The generalized facts for the population count Regular expression:
    - There will be no decimal numbers
    - digits seperated by comma or not
    - digits from 1 to 9 and zero can occur anywhere after first digit
    - can begin and end with a parenthesis
    - can have two white spaces before and after equals "=" -> (n = 16,273)
    - can have n or N referring to population and/or count
4) The full examples for each types of rules are as follows from <a href="https://www.pnas.org/doi/pdf/10.1073/pnas.2111091119">example input</a>:
    <ol>
        <li> 
        B is the unstandardized coefficient; rp is the partial standardized effect size for each coefficient. N = 25,718. Controlling: n = 8,368; no message: n = 8,790; autonomy supportive: n = 8,560. The controlling message was the reference group. We report three decimal places for p and rp and its 95% CI since our interval null is rp = –0.025 to 0.025 and two decimals for all other values. df, degree of freedom.
        </li>
        <li> 
        B is the unstandardized coefficient; rp is the partial standardized effect size for each coefficient. N = 23,554. Controlling: n = 7,688; no message: n = 8,059; autonomy supportive: n = 7,807. The controlling message was the reference group. We report three decimal places for p and rp and its 95% CI since our interval null is rp = –0.025 to 0.025 and two decimals for all other values. df, degree of freedomy.
        </li>
        </li>
        Of the total sample, 63.3% identified as female (n = 16,273), 33.6% identified as male (n = 8,636), 1.1% indicated that male and female categories did not fit for them (n = 288), and 2% preferred not to respond.
        </li>
    </ol>

5) Example Rules: 
