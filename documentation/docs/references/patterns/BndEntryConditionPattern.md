<!-- Auto generated file, do not make any changes here. -->

## BndEntryConditionPattern

### BndEntryConditionPattern Globally
```
Globally, it is always the case that after "R" holds for at least "5" time units, then "Q" holds
```

#### Countertraces
```
true;⌈R⌉ ∧ ℓ ≥ 5;⌈!Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEntryConditionPattern_Globally_0.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Globally_0.svg) | ![](../img/failure_paths/negative/BndEntryConditionPattern_Globally_0.svg) |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Globally_1.svg) | ![](../img/failure_paths/negative/BndEntryConditionPattern_Globally_1.svg) |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Globally_2.svg) |  |


### BndEntryConditionPattern Before
```
Before "Q", it is always the case that after "S" holds for at least "5" time units, then "R" holds
```

#### Countertraces
```
⌈!Q⌉;⌈(!Q && S)⌉ ∧ ℓ ≥ 5;⌈(!Q && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEntryConditionPattern_Before_0.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Before_0.svg) | ![](../img/failure_paths/negative/BndEntryConditionPattern_Before_0.svg) |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Before_1.svg) |  |


### BndEntryConditionPattern After
```
After "Q", it is always the case that after "S" holds for at least "5" time units, then "R" holds
```

#### Countertraces
```
true;⌈Q⌉;true;⌈S⌉ ∧ ℓ ≥ 5;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEntryConditionPattern_After_0.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_After_0.svg) | ![](../img/failure_paths/negative/BndEntryConditionPattern_After_0.svg) |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_After_1.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_After_2.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_After_3.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_After_4.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_After_5.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_After_6.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_After_7.svg) |  |


### BndEntryConditionPattern Between
```
Between "Q" and "R", it is always the case that after "T" holds for at least "5" time units, then "S" holds
```

#### Countertraces
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && T)⌉ ∧ ℓ ≥ 5;⌈(!R && !S)⌉;⌈!R⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEntryConditionPattern_Between_0.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Between_0.svg) | ![](../img/failure_paths/negative/BndEntryConditionPattern_Between_0.svg) |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Between_1.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Between_2.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Between_3.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Between_4.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Between_5.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Between_6.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Between_7.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Between_8.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Between_9.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Between_10.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_Between_11.svg) |  |


### BndEntryConditionPattern AfterUntil
```
After "Q" until "R", it is always the case that after "T" holds for at least "5" time units, then "S" holds
```

#### Countertraces
```
true;⌈Q⌉;⌈!R⌉;⌈(!R && T)⌉ ∧ ℓ ≥ 5;⌈(!R && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEntryConditionPattern_AfterUntil_0.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_AfterUntil_0.svg) | ![](../img/failure_paths/negative/BndEntryConditionPattern_AfterUntil_0.svg) |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_AfterUntil_1.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_AfterUntil_2.svg) |  |
| ![](../img/failure_paths/positive/BndEntryConditionPattern_AfterUntil_3.svg) |  |

