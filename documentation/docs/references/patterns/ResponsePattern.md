<!-- Auto generated file, do not make any changes here. -->

## ResponsePattern

### ResponsePattern Before
```
Before "Q", it is always the case that if "S" holds, then "R" eventually holds
```
```
Counterexample: ⌈!Q⌉;⌈(!Q && (!R && S))⌉;⌈(!Q && !R)⌉;⌈Q⌉;true
```

![](../img/patterns/ResponsePattern_Before.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
|  | ![](../img/failure_paths/negative/ResponsePattern_Before_0.svg) |


### ResponsePattern Between
```
Between "Q" and "R", it is always the case that if "T" holds, then "S" eventually holds
```
```
Counterexample: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && (!S && T))⌉;⌈(!R && !S)⌉;⌈R⌉;true
```

![](../img/patterns/ResponsePattern_Between.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
|  | ![](../img/failure_paths/negative/ResponsePattern_Between_0.svg) |
