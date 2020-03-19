<!-- Auto generated file, do not make any changes here. -->

## PrecedencePattern

### PrecedencePattern Globally
```
Globally, it is always the case that if "R" holds, then "Q" previously held
```
```
Counterexample: ⌈!Q⌉;⌈R⌉;true
```

![](../img/patterns/PrecedencePattern_Globally.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
|  | ![](../img/failure_paths/negative/PrecedencePattern_Globally_0.svg) |
|  | ![](../img/failure_paths/negative/PrecedencePattern_Globally_1.svg) |


### PrecedencePattern Before
```
Before "Q", it is always the case that if "S" holds, then "R" previously held
```
```
Counterexample: ⌈(!Q && !R)⌉;⌈(!Q && S)⌉;true
```

![](../img/patterns/PrecedencePattern_Before.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
|  | ![](../img/failure_paths/negative/PrecedencePattern_Before_0.svg) |


### PrecedencePattern After
```
After "Q", it is always the case that if "S" holds, then "R" previously held
```
```
Counterexample: true;⌈(Q && !R)⌉;⌈!R⌉;⌈S⌉;true
```

![](../img/patterns/PrecedencePattern_After.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
|  | ![](../img/failure_paths/negative/PrecedencePattern_After_0.svg) |


### PrecedencePattern Between
```
Between "Q" and "R", it is always the case that if "T" holds, then "S" previously held
```
```
Counterexample: true;⌈(Q && (!R && !S))⌉;⌈(!R && !S)⌉;⌈(!R && T)⌉;⌈!R⌉;⌈R⌉;true
```

![](../img/patterns/PrecedencePattern_Between.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
|  | ![](../img/failure_paths/negative/PrecedencePattern_Between_0.svg) |


### PrecedencePattern AfterUntil
```
After "Q" until "R", it is always the case that if "T" holds, then "S" previously held
```
```
Counterexample: true;⌈(Q && (!R && !S))⌉;⌈(!R && !S)⌉;⌈(!R && T)⌉;true
```

![](../img/patterns/PrecedencePattern_AfterUntil.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
|  | ![](../img/failure_paths/negative/PrecedencePattern_AfterUntil_0.svg) |

