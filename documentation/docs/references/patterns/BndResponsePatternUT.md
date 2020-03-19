<!-- Auto generated file, do not make any changes here. -->

## BndResponsePatternUT

### BndResponsePatternUT Globally
```
Globally, it is always the case that if "R" holds, then "Q" holds after at most "5" time units
```
```
Counterexample: true;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ > 5;true
```

![](../img/patterns/BndResponsePatternUT_Globally.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndResponsePatternUT_Globally_0.svg) |


### BndResponsePatternUT Before
```
Before "Q", it is always the case that if "S" holds, then "R" holds after at most "5" time units
```
```
Counterexample: ⌈!Q⌉;⌈(!Q && (!R && S))⌉;⌈(!Q && !R)⌉ ∧ ℓ > 5;true
```

![](../img/patterns/BndResponsePatternUT_Before.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndResponsePatternUT_Before_0.svg) |


### BndResponsePatternUT After
```
After "Q", it is always the case that if "S" holds, then "R" holds after at most "5" time units
```
```
Counterexample: true;⌈Q⌉;true;⌈(!R && S)⌉;⌈!R⌉ ∧ ℓ > 5;true
```

![](../img/patterns/BndResponsePatternUT_After.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndResponsePatternUT_After_0.svg) |


### BndResponsePatternUT Between
```
Between "Q" and "R", it is always the case that if "T" holds, then "S" holds after at most "5" time units
```
```
Counterexample: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && (!S && T))⌉;⌈(!R && !S)⌉ ∧ ℓ > 5;⌈!R⌉;⌈R⌉;true
```

![](../img/patterns/BndResponsePatternUT_Between.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndResponsePatternUT_Between_0.svg) |


### BndResponsePatternUT AfterUntil
```
After "Q" until "R", it is always the case that if "T" holds, then "S" holds after at most "5" time units
```
```
Counterexample: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && (!S && T))⌉;⌈(!R && !S)⌉ ∧ ℓ > 5;true
```

![](../img/patterns/BndResponsePatternUT_AfterUntil.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndResponsePatternUT_AfterUntil_0.svg) |
