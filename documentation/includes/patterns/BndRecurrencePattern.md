<!-- Auto generated file, do not make any changes here. -->

## BndRecurrencePattern

### BndRecurrencePattern Globally
```
Globally, it is always the case that "Q" holds at least every "5" time units
```

#### Countertraces
```
true;⌈!Q⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/BndRecurrencePattern_Globally_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
|  | ![](../img/failure_paths/negative/BndRecurrencePattern_Globally_0.svg) |


### BndRecurrencePattern Before
```
Before "Q", it is always the case that "R" holds at least every "5" time units
```

#### Countertraces
```
⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/BndRecurrencePattern_Before_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
|  | ![](../img/failure_paths/negative/BndRecurrencePattern_Before_0.svg) |


### BndRecurrencePattern After
```
After "Q", it is always the case that "R" holds at least every "5" time units
```

#### Countertraces
```
true;⌈Q⌉;true;⌈!R⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/BndRecurrencePattern_After_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
|  | ![](../img/failure_paths/negative/BndRecurrencePattern_After_0.svg) |


### BndRecurrencePattern Between
```
Between "Q" and "R", it is always the case that "S" holds at least every "5" time units
```

#### Countertraces
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !S)⌉ ∧ ℓ > 5;⌈!R⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndRecurrencePattern_Between_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/BndRecurrencePattern_Between_0.svg) | ![](../img/failure_paths/negative/BndRecurrencePattern_Between_0.svg) |
| ![](../img/failure_paths/positive/BndRecurrencePattern_Between_1.svg) |  |
| ![](../img/failure_paths/positive/BndRecurrencePattern_Between_2.svg) |  |
| ![](../img/failure_paths/positive/BndRecurrencePattern_Between_3.svg) |  |
| ![](../img/failure_paths/positive/BndRecurrencePattern_Between_4.svg) |  |
| ![](../img/failure_paths/positive/BndRecurrencePattern_Between_5.svg) |  |


### BndRecurrencePattern AfterUntil
```
After "Q" until "R", it is always the case that "S" holds at least every "5" time units
```

#### Countertraces
```
true;⌈Q⌉;⌈!R⌉;⌈(!R && !S)⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/BndRecurrencePattern_AfterUntil_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
|  | ![](../img/failure_paths/negative/BndRecurrencePattern_AfterUntil_0.svg) |

