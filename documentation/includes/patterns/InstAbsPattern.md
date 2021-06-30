<!-- Auto generated file, do not make any changes here. -->

## InstAbsPattern

### InstAbsPattern Globally
```
Globally, it is never the case that "Q" holds
```

#### Countertraces
```
true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/InstAbsPattern_Globally_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/InstAbsPattern_Globally_0.svg) | ![](../img/failure_paths/negative/InstAbsPattern_Globally_0.svg) |
|  | ![](../img/failure_paths/negative/InstAbsPattern_Globally_1.svg) |


### InstAbsPattern After
```
After "Q", it is never the case that "R" holds
```

#### Countertraces
```
true;⌈Q⌉;true;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/InstAbsPattern_After_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/InstAbsPattern_After_0.svg) | ![](../img/failure_paths/negative/InstAbsPattern_After_0.svg) |
| ![](../img/failure_paths/positive/InstAbsPattern_After_1.svg) | ![](../img/failure_paths/negative/InstAbsPattern_After_1.svg) |


### InstAbsPattern Between
```
Between "Q" and "R", it is never the case that "S" holds
```

#### Countertraces
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && S)⌉;⌈!R⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/InstAbsPattern_Between_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/InstAbsPattern_Between_0.svg) | ![](../img/failure_paths/negative/InstAbsPattern_Between_0.svg) |
| ![](../img/failure_paths/positive/InstAbsPattern_Between_1.svg) |  |
| ![](../img/failure_paths/positive/InstAbsPattern_Between_2.svg) |  |
| ![](../img/failure_paths/positive/InstAbsPattern_Between_3.svg) |  |


### InstAbsPattern AfterUntil
```
After "Q" until "R", it is never the case that "S" holds
```

#### Countertraces
```
true;⌈Q⌉;⌈!R⌉;⌈(!R && S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/InstAbsPattern_AfterUntil_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/InstAbsPattern_AfterUntil_0.svg) | ![](../img/failure_paths/negative/InstAbsPattern_AfterUntil_0.svg) |
| ![](../img/failure_paths/positive/InstAbsPattern_AfterUntil_1.svg) |  |

