<!-- Auto generated file, do not make any changes here. -->

## PrecedenceChain12Pattern

### PrecedenceChain12Pattern Globally
```
Globally, it is always the case that if "S" holds and is succeeded by "R", then "Q" previously held
```
```
Counterexample: ⌈!S⌉;⌈R⌉;true;⌈Q⌉;true
```

![](../img/patterns/PrecedenceChain12Pattern_Globally.svg)


### PrecedenceChain12Pattern Before
```
Before "Q", it is always the case that if "T" holds and is succeeded by "S", then "R" previously held
```
```
Counterexample: ⌈(!Q && !T)⌉;⌈(!Q && (S && !T))⌉;⌈!Q⌉;⌈(!Q && R)⌉;true
```

![](../img/patterns/PrecedenceChain12Pattern_Before.svg)


### PrecedenceChain12Pattern After
```
After "Q", it is always the case that if "T" holds and is succeeded by "S", then "R" previously held
```
```
Counterexample: ⌈!T⌉;⌈(Q && !T)⌉;⌈!T⌉;⌈(S && !T)⌉;true;⌈R⌉;true
```

![](../img/patterns/PrecedenceChain12Pattern_After.svg)


### PrecedenceChain12Pattern Between
```
Between "Q" and "R", it is always the case that if "U" holds and is succeeded by "T", then "S" previously held
```
```
Counterexample: ⌈!U⌉;⌈(Q && (!R && !U))⌉;⌈(!R && !U)⌉;⌈(!R && (T && !U))⌉;⌈!R⌉;⌈(!R && S)⌉;⌈!R⌉;⌈R⌉;true
```

![](../img/patterns/PrecedenceChain12Pattern_Between.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
| ![](../img/failure_paths/PrecedenceChain12Pattern_Between_0.svg) | |
| ![](../img/failure_paths/PrecedenceChain12Pattern_Between_1.svg) | |
| ![](../img/failure_paths/PrecedenceChain12Pattern_Between_2.svg) | |
| ![](../img/failure_paths/PrecedenceChain12Pattern_Between_3.svg) | |
| ![](../img/failure_paths/PrecedenceChain12Pattern_Between_4.svg) | |


### PrecedenceChain12Pattern AfterUntil
```
After "Q" until "R", it is always the case that if "U" holds and is succeeded by "T", then "S" previously held
```
```
Counterexample: ⌈!U⌉;⌈(Q && (!R && !U))⌉;⌈(!R && !U)⌉;⌈(!R && (T && !U))⌉;⌈!R⌉;⌈(!R && S)⌉;true
```

![](../img/patterns/PrecedenceChain12Pattern_AfterUntil.svg)

