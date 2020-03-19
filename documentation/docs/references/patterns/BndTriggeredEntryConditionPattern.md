<!-- Auto generated file, do not make any changes here. -->

## BndTriggeredEntryConditionPattern

### BndTriggeredEntryConditionPattern Globally
```
Globally, it is always the case that after "Q" holds for at least "5" time units and "R" holds, then "S" holds
```
```
Counterexample: true;⌈Q⌉ ∧ ℓ ≥ 5;⌈(Q && (R && !S))⌉;true
```

![](../img/patterns/BndTriggeredEntryConditionPattern_Globally.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndTriggeredEntryConditionPattern_Globally_0.svg) |
|  | ![](../img/failure_paths/negative/BndTriggeredEntryConditionPattern_Globally_1.svg) |

