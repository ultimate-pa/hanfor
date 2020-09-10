<!-- Auto generated file, do not make any changes here. -->

## PrecedenceChain12Pattern

### PrecedenceChain12Pattern Globally
```
Globally, it is always the case that if "S" holds and is succeeded by "R", then "Q" previously held
```

```
Countertraces: (⌈!Q⌉;⌈S⌉;true;⌈R⌉;true)
```

![](../img/patterns/PrecedenceChain12Pattern_Globally_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Globally_0.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Globally_1.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Globally_2.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Globally_3.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Globally_4.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Globally_5.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Globally_6.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Globally_7.svg) |  |


### PrecedenceChain12Pattern Before
```
Before "Q", it is always the case that if "T" holds and is succeeded by "S", then "R" previously held
```

```
Countertraces: (⌈(!Q && !R)⌉;⌈(!Q && T)⌉;⌈!Q⌉;⌈(!Q && S)⌉;true)
```

![](../img/patterns/PrecedenceChain12Pattern_Before_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Before_0.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Before_1.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Before_2.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Before_3.svg) |  |


### PrecedenceChain12Pattern After
```
After "Q", it is always the case that if "T" holds and is succeeded by "S", then "R" previously held
```

```
Countertraces: (true;⌈Q⌉;⌈!R⌉;⌈T⌉;true;⌈S⌉;true)
```

![](../img/patterns/PrecedenceChain12Pattern_After_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_0.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_1.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_2.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_3.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_4.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_5.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_6.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_7.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_8.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_9.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_10.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_11.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_12.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_13.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_14.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_15.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_16.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_17.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_18.svg) |  |


### PrecedenceChain12Pattern Between
```
Between "Q" and "R", it is always the case that if "U" holds and is succeeded by "T", then "S" previously held
```

```
Countertraces: (true;⌈(Q && !R)⌉;⌈(!R && !S)⌉;⌈(!R && U)⌉;⌈!R⌉;⌈(!R && T)⌉;⌈!R⌉;⌈R⌉;true)
```

![](../img/patterns/PrecedenceChain12Pattern_Between_0.svg)


### PrecedenceChain12Pattern AfterUntil
```
After "Q" until "R", it is always the case that if "U" holds and is succeeded by "T", then "S" previously held
```

```
Countertraces: (true;⌈Q⌉;⌈(!R && !S)⌉;⌈(!R && U)⌉;⌈!R⌉;⌈(!R && T)⌉;true)
```

![](../img/patterns/PrecedenceChain12Pattern_AfterUntil_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_AfterUntil_0.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_AfterUntil_1.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_AfterUntil_2.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_AfterUntil_3.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_AfterUntil_4.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_AfterUntil_5.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_AfterUntil_6.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain12Pattern_AfterUntil_7.svg) |  |

