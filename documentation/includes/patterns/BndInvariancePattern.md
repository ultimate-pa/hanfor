<!-- Auto generated file, do not make any changes here. -->

## BndInvariancePattern

### BndInvariancePattern Globally
```
Globally, it is always the case that if "R" holds, then "Q" holds for at least "5" time units
```

#### Countertraces
```
true;⌈R⌉;⌈true⌉ ∧ ℓ < 5;⌈!Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndInvariancePattern_Globally_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/BndInvariancePattern_Globally_0.svg) | ![](../img/failure_paths/negative/BndInvariancePattern_Globally_0.svg) |
| ![](../img/failure_paths/positive/BndInvariancePattern_Globally_1.svg) |  |


### BndInvariancePattern Before
```
Before "Q", it is always the case that if "S" holds, then "R" holds for at least "5" time units
```

#### Countertraces
```
⌈!Q⌉;⌈(!Q && S)⌉;⌈!Q⌉ ∧ ℓ < 5;⌈(!Q && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndInvariancePattern_Before_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/BndInvariancePattern_Before_0.svg) | ![](../img/failure_paths/negative/BndInvariancePattern_Before_0.svg) |
| ![](../img/failure_paths/positive/BndInvariancePattern_Before_1.svg) |  |


### BndInvariancePattern After
```
After "Q", it is always the case that if "S" holds, then "R" holds for at least "5" time units
```

#### Countertraces
```
true;⌈Q⌉;true;⌈S⌉;⌈true⌉ ∧ ℓ < 5;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndInvariancePattern_After_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/BndInvariancePattern_After_0.svg) | ![](../img/failure_paths/negative/BndInvariancePattern_After_0.svg) |
| ![](../img/failure_paths/positive/BndInvariancePattern_After_1.svg) |  |
| ![](../img/failure_paths/positive/BndInvariancePattern_After_2.svg) |  |
| ![](../img/failure_paths/positive/BndInvariancePattern_After_3.svg) |  |


### BndInvariancePattern Between
```
Between "Q" and "R", it is always the case that if "T" holds, then "S" holds for at least "5" time units
```

#### Countertraces
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && T)⌉;⌈!R⌉ ∧ ℓ < 5;⌈(!R && !S)⌉;⌈!R⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndInvariancePattern_Between_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/BndInvariancePattern_Between_0.svg) | ![](../img/failure_paths/negative/BndInvariancePattern_Between_0.svg) |
| ![](../img/failure_paths/positive/BndInvariancePattern_Between_1.svg) |  |
| ![](../img/failure_paths/positive/BndInvariancePattern_Between_2.svg) |  |
| ![](../img/failure_paths/positive/BndInvariancePattern_Between_3.svg) |  |
| ![](../img/failure_paths/positive/BndInvariancePattern_Between_4.svg) |  |
| ![](../img/failure_paths/positive/BndInvariancePattern_Between_5.svg) |  |
| ![](../img/failure_paths/positive/BndInvariancePattern_Between_6.svg) |  |
| ![](../img/failure_paths/positive/BndInvariancePattern_Between_7.svg) |  |


### BndInvariancePattern AfterUntil
```
After "Q" until "R", it is always the case that if "T" holds, then "S" holds for at least "5" time units
```

#### Countertraces
```
true;⌈Q⌉;⌈!R⌉;⌈(!R && T)⌉;⌈!R⌉ ∧ ℓ < 5;⌈(!R && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndInvariancePattern_AfterUntil_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/BndInvariancePattern_AfterUntil_0.svg) | ![](../img/failure_paths/negative/BndInvariancePattern_AfterUntil_0.svg) |
| ![](../img/failure_paths/positive/BndInvariancePattern_AfterUntil_1.svg) |  |
| ![](../img/failure_paths/positive/BndInvariancePattern_AfterUntil_2.svg) |  |
| ![](../img/failure_paths/positive/BndInvariancePattern_AfterUntil_3.svg) |  |

