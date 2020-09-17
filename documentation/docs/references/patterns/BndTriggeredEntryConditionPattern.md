<!-- Auto generated file, do not make any changes here. -->

## BndTriggeredEntryConditionPattern

### BndTriggeredEntryConditionPattern Globally
```
Globally, it is always the case that after "S" holds for at least "5" time units and "R" holds, then "Q" holds
```

#### Countertraces
```
true;⌈Q⌉ ∧ ℓ ≥ 5;⌈(Q && (R && !S))⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndTriggeredEntryConditionPattern_Globally_0.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/BndTriggeredEntryConditionPattern_Globally_0.svg) | ![](../img/failure_paths/negative/BndTriggeredEntryConditionPattern_Globally_0.svg) |
| ![](../img/failure_paths/positive/BndTriggeredEntryConditionPattern_Globally_1.svg) | ![](../img/failure_paths/negative/BndTriggeredEntryConditionPattern_Globally_1.svg) |

