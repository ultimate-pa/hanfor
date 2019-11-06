toc_depth: 4

# Duration Calculus

Hanfor automatically translates requirements, that are given in the [specification language](../introduction/index.md#specification-language "Specification Language"), into duration calculus (dc).
To be able to understand the different patterns that are supported by Hanfor, it is often useful to consider their counterexample traces.

Below, you find a short guide that should enable you to read and interpret the duration calculus formulae provided within this documentation. It aims to give you an intuitive insight into the very basics of duration calculus.


Duration calculus uses time intervalls to concisely express sequential behavior. Assuming that you are familiar with the basic concept of boolean logic, there are only three additional operators that we should have a look at.



!!! note "Everywhere-Operator: [ ]"
    The Everywhere-operator [ ] applied to an expression describes an interval of arbitrary length in which the embraced expression holds. 
    If the operator is kept empty, it describes a point interval (length = 0).

    Consider the dc-formula: `[A]`

    It describes a behavior where first 'A' holds , then 'B' holds, and finally 'C' holds.<br/>
    All intervals may have an arbitrary length > 0, as there is no explicit  constraint on the durations.


!!! note "Length-Operator: l"
    The length-operator l is used to measure the length of an interval.<br/>

    Consider the dc-formula: `[A] && l = 5`


    It describes an intervall with a length of 5 time units in which expression 'A' holds.<br/>


!!! note "Chop-Operator: ;"
    The chop-operator ; "chops" larger time intervals into smaller subintervals.<br/>

    Consider the dc-formula: `[A];[B];[C]`

    It describes a behavior where first 'A' holds , then 'B' holds, and finally 'C' holds.<br/>
    All intervals may have an arbitrary length > 0 time units, as there is no explicit  constraint on their duration.

## Examples
In the following, you find some examples. In each we give a property in the specification language, a corresponding dc-formula, and a short description.

!!! example "Example 1: Eventually 'A' holds."
    * `true, [A], true`
    * The subintervall in which 'A' holds is both preceeded and succeeded by an arbitrary intervall specified by *true*.

!!! example "Example 2: Eventually 'A' holds for at least 5 time units."
    * `true, [A] && l >= 5, true`
    * As before, the subintervall in which 'A' holds is both preceeded and succeeded by an arbitrary intervall specified by *true*. Additionally, the duration of the intervall in which 'A' holds must be greater or equal to 5 time units.

!!! example "Example 3:  Eventually 'A' holds for at most 7 time units and is succeeded by both 'B' and 'C'."
    * `true, [A] && l <= 7, true; [B && C]; true`
    * The subintervall in which 'A' holds must not be longer than 7 time units. Additionally, it must be followed by an interval of arbitrary length in which both 'B' and 'C' hold.
