<!-- Auto generated file, do not make any changes here. -->

## ResponsePattern

### ResponsePattern Before
```
Before "Q", it is always the case that if "S" holds, then "R" eventually holds
```

#### Countertraces
```
⌈!Q⌉;⌈(!Q && (!R && S))⌉;⌈(!Q && !R)⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponsePattern_Before_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/ResponsePattern_Before_0.svg) | ![](../img/failure_paths/negative/ResponsePattern_Before_0.svg) |
| ![](../img/failure_paths/positive/ResponsePattern_Before_1.svg) |  |


### ResponsePattern Between
```
Between "Q" and "R", it is always the case that if "T" holds, then "S" eventually holds
```

#### Countertraces
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && (!S && T))⌉;⌈(!R && !S)⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponsePattern_Between_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/ResponsePattern_Between_0.svg) | ![](../img/failure_paths/negative/ResponsePattern_Between_0.svg) |
| ![](../img/failure_paths/positive/ResponsePattern_Between_1.svg) |  |
| ![](../img/failure_paths/positive/ResponsePattern_Between_2.svg) |  |
| ![](../img/failure_paths/positive/ResponsePattern_Between_3.svg) |  |


### ResponsePattern AfterUntil
```
After "Q" until "R", it is always the case that if "T" holds, then "S" eventually holds
```

#### Countertraces
```
true;⌈Q⌉;⌈!R⌉;⌈(!R && (!S && T))⌉;⌈(!R && !S)⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponsePattern_AfterUntil_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/ResponsePattern_AfterUntil_0.svg) |  |
| ![](../img/failure_paths/positive/ResponsePattern_AfterUntil_1.svg) |  |
| ![](../img/failure_paths/positive/ResponsePattern_AfterUntil_2.svg) |  |
| ![](../img/failure_paths/positive/ResponsePattern_AfterUntil_3.svg) |  |

