<!-- Auto generated file, do not make any changes here. -->

## PrecedencePattern

### PrecedencePattern Globally
```
Globally, it is always the case that if "R" holds, then "Q" previously held
```

```
Countertraces:
⌈!Q⌉;⌈R⌉;true
```

![](../img/patterns/PrecedencePattern_Globally_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/PrecedencePattern_Globally_0.svg) | ![](../img/failure_paths/negative/PrecedencePattern_Globally_0.svg) |
| ![](../img/failure_paths/positive/PrecedencePattern_Globally_1.svg) | ![](../img/failure_paths/negative/PrecedencePattern_Globally_1.svg) |


### PrecedencePattern Before
```
Before "Q", it is always the case that if "S" holds, then "R" previously held
```

```
Countertraces:
⌈(!Q && !R)⌉;⌈(!Q && S)⌉;true
```

![](../img/patterns/PrecedencePattern_Before_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/PrecedencePattern_Before_0.svg) | ![](../img/failure_paths/negative/PrecedencePattern_Before_0.svg) |


### PrecedencePattern After
```
After "Q", it is always the case that if "S" holds, then "R" previously held
```

```
Countertraces:
true;⌈Q⌉;⌈!R⌉;⌈S⌉;true
```

![](../img/patterns/PrecedencePattern_After_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/PrecedencePattern_After_0.svg) | ![](../img/failure_paths/negative/PrecedencePattern_After_0.svg) |
| ![](../img/failure_paths/positive/PrecedencePattern_After_1.svg) |  |
| ![](../img/failure_paths/positive/PrecedencePattern_After_2.svg) |  |
| ![](../img/failure_paths/positive/PrecedencePattern_After_3.svg) |  |


### PrecedencePattern Between
```
Between "Q" and "R", it is always the case that if "T" holds, then "S" previously held
```

```
Countertraces:
true;⌈(Q && (!R && !S))⌉;⌈(!R && !S)⌉;⌈(!R && T)⌉;⌈!R⌉;⌈R⌉;true
```

![](../img/patterns/PrecedencePattern_Between_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/PrecedencePattern_Between_0.svg) | ![](../img/failure_paths/negative/PrecedencePattern_Between_0.svg) |
| ![](../img/failure_paths/positive/PrecedencePattern_Between_1.svg) |  |
| ![](../img/failure_paths/positive/PrecedencePattern_Between_2.svg) |  |
| ![](../img/failure_paths/positive/PrecedencePattern_Between_3.svg) |  |
| ![](../img/failure_paths/positive/PrecedencePattern_Between_4.svg) |  |
| ![](../img/failure_paths/positive/PrecedencePattern_Between_5.svg) |  |


### PrecedencePattern AfterUntil
```
After "Q" until "R", it is always the case that if "T" holds, then "S" previously held
```

```
Countertraces:
true;⌈Q⌉;⌈(!R && !S)⌉;⌈(!R && T)⌉;true
```

![](../img/patterns/PrecedencePattern_AfterUntil_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/PrecedencePattern_AfterUntil_0.svg) | ![](../img/failure_paths/negative/PrecedencePattern_AfterUntil_0.svg) |
| ![](../img/failure_paths/positive/PrecedencePattern_AfterUntil_1.svg) |  |

