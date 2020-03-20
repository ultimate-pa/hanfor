<!-- Auto generated file, do not make any changes here. -->

## BndEntryConditionPattern

### BndEntryConditionPattern Globally
```
Globally, it is always the case that after "R" holds for at least "5" time units, then "Q" holds
```
```
Countertraces: true;⌈R⌉ ∧ ℓ ≥ 5;⌈!Q⌉;true
```

![](../img/patterns/BndEntryConditionPattern_Globally.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndEntryConditionPattern_Globally_0.svg) |
|  | ![](../img/failure_paths/negative/BndEntryConditionPattern_Globally_1.svg) |


### BndEntryConditionPattern Before
```
Before "Q", it is always the case that after "S" holds for at least "5" time units, then "R" holds
```
```
Countertraces: ⌈!Q⌉;⌈(!Q && S)⌉ ∧ ℓ ≥ 5;⌈(!Q && !R)⌉;true
```

![](../img/patterns/BndEntryConditionPattern_Before.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Before_0.svg) | ![](../img/failure_paths/negative/BndEntryConditionPattern_Before_0.svg) |


### BndEntryConditionPattern After
```
After "Q", it is always the case that after "S" holds for at least "5" time units, then "R" holds
```
```
Countertraces: true;⌈Q⌉;true;⌈S⌉ ∧ ℓ ≥ 5;⌈!R⌉;true
```

![](../img/patterns/BndEntryConditionPattern_After.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndEntryConditionPattern_After_0.svg) |


### BndEntryConditionPattern Between
```
Between "Q" and "R", it is always the case that after "T" holds for at least "5" time units, then "S" holds
```
```
Countertraces: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && T)⌉ ∧ ℓ ≥ 5;⌈(!R && !S)⌉;⌈!R⌉;⌈R⌉;true
```

![](../img/patterns/BndEntryConditionPattern_Between.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndEntryConditionPattern_Between_0.svg) |


### BndEntryConditionPattern AfterUntil
```
After "Q" until "R", it is always the case that after "T" holds for at least "5" time units, then "S" holds
```
```
Countertraces: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && T)⌉ ∧ ℓ ≥ 5;⌈(!R && !S)⌉;true
```

![](../img/patterns/BndEntryConditionPattern_AfterUntil.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_AfterUntil_0.svg) | ![](../img/failure_paths/negative/BndEntryConditionPattern_AfterUntil_0.svg) |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_AfterUntil_1.svg) |  |

