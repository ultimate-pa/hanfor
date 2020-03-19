<!-- Auto generated file, do not make any changes here. -->

## BndEntryConditionPattern

### BndEntryConditionPattern Globally
```
Globally, it is always the case that after "R" holds for at least "5" time units, then "Q" holds
```
```
Counterexample: true;⌈R⌉ ∧ ℓ ≥ 5;⌈!Q⌉;true
```

![](../img/patterns/BndEntryConditionPattern_Globally.svg)


### BndEntryConditionPattern Before
```
Before "Q", it is always the case that after "S" holds for at least "5" time units, then "R" holds
```
```
Counterexample: ⌈!Q⌉;⌈(!Q && S)⌉ ∧ ℓ ≥ 5;⌈(!Q && !R)⌉;true
```

![](../img/patterns/BndEntryConditionPattern_Before.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Before_0.svg) |  |


### BndEntryConditionPattern After
```
After "Q", it is always the case that after "S" holds for at least "5" time units, then "R" holds
```
```
Counterexample: true;⌈Q⌉;true;⌈S⌉ ∧ ℓ ≥ 5;⌈!R⌉;true
```

![](../img/patterns/BndEntryConditionPattern_After.svg)


### BndEntryConditionPattern Between
```
Between "Q" and "R", it is always the case that after "T" holds for at least "5" time units, then "S" holds
```
```
Counterexample: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && T)⌉ ∧ ℓ ≥ 5;⌈(!R && !S)⌉;⌈!R⌉;⌈R⌉;true
```

![](../img/patterns/BndEntryConditionPattern_Between.svg)


### BndEntryConditionPattern AfterUntil
```
After "Q" until "R", it is always the case that after "T" holds for at least "5" time units, then "S" holds
```
```
Counterexample: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && T)⌉ ∧ ℓ ≥ 5;⌈(!R && !S)⌉;true
```

![](../img/patterns/BndEntryConditionPattern_AfterUntil.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_AfterUntil_0.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_AfterUntil_1.svg) |  |

