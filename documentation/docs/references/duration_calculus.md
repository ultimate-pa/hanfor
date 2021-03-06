toc_depth: 4

# Duration Calculus

Hanfor automatically translates requirements, that are given in the natural-language-style [specification language](../introduction/index.md#specification-language "Specification Language"), into Counterexample Formulae, a small and comprehensible subset of Duration Calculus (DC).

This short guide should enable you to read and interpret the Duration Calculus formulae provided within this documentation. It aims to give you an intuitive insight into the small fragment of Duration Calculus that we use in our tool.

Duration Calculus uses time intervalls to express sequential behavior. Assuming that you are familiar with the basic concept of Boolean logic, there are only three additional operators that need to be introduced.



!!! note "Everywhere-Operator: ⌈ ⌉"
    The everywhere-operator applied to an expression describes an interval of arbitrary length (length > 0) in which the embraced expression holds. 
    If the operator is kept empty, it describes a point interval (length = 0).

    Let 'A' be an expression. Consider the DC-formula: `⌈A⌉`

    It describes an interval of arbitrary length (length > 0) in which expression 'A' holds.<br/>


!!! note "Length-Operator: ℓ"
    The length-operator is used to measure the length of an interval.<br/>

    Let 'A' be an expression. Consider the DC-formula: `⌈A⌉ ∧ ℓ = 5`

    It describes an interval with a length of 5 time units in which expression 'A' holds.<br/>


!!! note "Chop-Operator: ;"
    The chop-operator "chops" larger time intervals into smaller subintervals.<br/>

    Let 'A', 'B', and 'C' be expressions. Consider the DC-formula: `⌈A⌉; ⌈B⌉; ⌈C⌉`

    It describes a behavior where first expression 'A' holds , then exprression 'B' holds, and finally expression 'C' holds.<br/>
    Note: All intervals may have an arbitrary length > 0 time units, as there is no explicit  constraint on their duration.


## Counterexample Formulas
Now that we have looked at some necessary building blocks of DC, we can look at counterexample formulas. 

!!! note "Counterexample Formula"
    Formally, a counterexample formula Ψ is a DC-formula of the form:
    ` Ψ = (⌈e1⌉ ∧ ℓ ~ t1); ... ;(⌈ek⌉ ∧ ℓ ~ tk); true ` , <br/>
    where `e1` to `ek` represent state expressions, `t1` to `tk` are non-zero durations, and `~ ∊ [≤,≥]`.

In other words, the counterexample formula exactly describes the undesired behavior relative to the given requirement. 

In the following, you find some examples. In each we give a property in the natural-language-style specification language, the counterexample DC-formula describing the undesired behavior, and a short explanation.

!!! example "Example 1:"
    * Globally, it is always the case that 'Q' holds.
    <br/><br/>
    * Counterexample: `(true; ⌈!Q⌉; true)`
    <br/><br/>
    * The counterexample DC-formula describes all behaviors that violate the given specification. In this example, the requirement is violated if there is an interval in which 'Q' does not hold.

!!! example "Example 2:"
    * Before 'Q', it is always the case that 'R' holds at least every '5' time units
    <br/><br/>
    * Counterexample: `(⌈!Q⌉; ⌈(!Q && !R)⌉ ∧ ℓ > 5; true)`
    <br/><br/>
    * The requirement can only be violated within its scope. All countertraces therefore have in common that '!Q' holds until the violation occured. The requirement is violated if '!R' holds longer than 5 time units.

!!! example "Example 3:"
    * After 'Q', it is always the case that once 'R' becomes satisfied, it holds for less than '5' time units.
    <br/><br/>
    * Counterexample: `(true; ⌈Q⌉; true; ⌈!R⌉; ⌈R⌉ ∧ ℓ ≥ 5; true)`
    <br/><br/>
    * The requirement can only be violated within its scope. All countertraces therefore have in common that 'Q' must hold before the violation occurs. 'R' becomes satisfied, when it toggles from *false* to *true*. The requirement is violated if 'R' holds for at least 5 time units.
