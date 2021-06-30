<!-- Auto generated file, do not make any changes here. -->

## BndExistencePattern

### BndExistencePattern Globally
```
Globally, transitions to states in which "Q" holds occur at most twice
```

#### Countertraces
```
true;⌈Q⌉;⌈!Q⌉;⌈Q⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndExistencePattern_Globally_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
|  | ![](../img/failure_paths/negative/BndExistencePattern_Globally_0.svg) |


### BndExistencePattern Before
```
Before "Q", transitions to states in which "R" holds occur at most twice
```

#### Countertraces
```
⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndExistencePattern_Before_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
|  | ![](../img/failure_paths/negative/BndExistencePattern_Before_0.svg) |


### BndExistencePattern After
```
After "Q", transitions to states in which "R" holds occur at most twice
```

#### Countertraces
```
true;⌈Q⌉;true;⌈R⌉;⌈!R⌉;⌈R⌉;⌈!R⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndExistencePattern_After_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
|  | ![](../img/failure_paths/negative/BndExistencePattern_After_0.svg) |


### BndExistencePattern Between
```
Between "Q" and "R", transitions to states in which "S" holds occur at most twice
```

#### Countertraces
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && S)⌉;⌈(!R && !S)⌉;⌈(!R && S)⌉;⌈(!R && !S)⌉;⌈(!R && S)⌉;⌈!R⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndExistencePattern_Between_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
|  | ![](../img/failure_paths/negative/BndExistencePattern_Between_0.svg) |


### BndExistencePattern AfterUntil
```
After "Q" until "R", transitions to states in which "S" holds occur at most twice
```

#### Countertraces
```
true;⌈Q⌉;⌈!R⌉;⌈(!R && S)⌉;⌈(!R && !S)⌉;⌈(!R && S)⌉;⌈(!R && !S)⌉;⌈(!R && S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndExistencePattern_AfterUntil_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
|  | ![](../img/failure_paths/negative/BndExistencePattern_AfterUntil_0.svg) |

