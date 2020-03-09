<!-- Auto generated file, do not make any changes here. -->

## MaxDurationPattern

### MaxDurationPattern Globally
```
Globally, it is always the case that once "Q" becomes satisfied, it holds for less than "5" time units
```
```
Counterexample: true;⌈Q⌉ ∧ ℓ ≥ 5;true
```

![](../img/patterns/MaxDurationPattern_Globally.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
| ![](../img/failure_paths/MaxDurationPattern_Globally_0.svg) | |


### MaxDurationPattern Before
```
Before "Q", it is always the case that once "R" becomes satisfied, it holds for less than "5" time units
```
```
Counterexample: ⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;true
```

![](../img/patterns/MaxDurationPattern_Before.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
| ![](../img/failure_paths/MaxDurationPattern_Before_0.svg) | |


### MaxDurationPattern After
```
After "Q", it is always the case that once "R" becomes satisfied, it holds for less than "5" time units
```
```
Counterexample: true;⌈Q⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ ≥ 5;true
```

![](../img/patterns/MaxDurationPattern_After.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
| ![](../img/failure_paths/MaxDurationPattern_After_0.svg) | |
| ![](../img/failure_paths/MaxDurationPattern_After_1.svg) | |


### MaxDurationPattern Between
```
Between "Q" and "R", it is always the case that once "S" becomes satisfied, it holds for less than "5" time units
```
```
Counterexample: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && S)⌉ ∧ ℓ ≥ 5;⌈!R⌉;⌈R⌉;true
```

![](../img/patterns/MaxDurationPattern_Between.svg)


### MaxDurationPattern AfterUntil
```
After "Q" until "R", it is always the case that once "S" becomes satisfied, it holds for less than "5" time units
```
```
Counterexample: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && S)⌉ ∧ ℓ ≥ 5;true
```

![](../img/patterns/MaxDurationPattern_AfterUntil.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
| ![](../img/failure_paths/MaxDurationPattern_AfterUntil_0.svg) | |
| ![](../img/failure_paths/MaxDurationPattern_AfterUntil_1.svg) | |

