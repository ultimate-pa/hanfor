<!-- Auto generated file, do not make any changes here. -->

## BndTriggeredEntryConditionPattern

### BndTriggeredEntryConditionPattern Globally
```
Globally, it is always the case that after "Q" holds for at least "5" time units and "R" holds, then "S" holds
```

```
Countertraces: (true;⌈Q⌉ ∧ ℓ ≥ 5;⌈(Q && (R && !S))⌉;true)
```

![](../img/patterns/BndTriggeredEntryConditionPattern_Globally_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/BndTriggeredEntryConditionPattern_Globally_0.svg) | ![](../img/failure_paths/negative/BndTriggeredEntryConditionPattern_Globally_0.svg) |
|  | ![](../img/failure_paths/negative/BndTriggeredEntryConditionPattern_Globally_1.svg) |

