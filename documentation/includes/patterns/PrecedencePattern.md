<!-- Auto generated file, do not make any changes here. -->

## PrecedencePattern

### PrecedencePattern Globally
```
Globally, it is always the case that if "R" holds, then "S" previously held
```

#### Countertraces
```
⌈!S⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedencePattern_Globally_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
|  | ![](../img/failure_paths/negative/PrecedencePattern_Globally_0.svg) |
|  | ![](../img/failure_paths/negative/PrecedencePattern_Globally_1.svg) |


### PrecedencePattern Before
```
Before "P", it is always the case that if "R" holds, then "S" previously held
```

#### Countertraces
```
⌈(!P && !S)⌉;⌈(!P && R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedencePattern_Before_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
|  | ![](../img/failure_paths/negative/PrecedencePattern_Before_0.svg) |


### PrecedencePattern After
```
After "P", it is always the case that if "R" holds, then "S" previously held
```

#### Countertraces
```
true;⌈P⌉;⌈!S⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedencePattern_After_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
|  | ![](../img/failure_paths/negative/PrecedencePattern_After_0.svg) |


### PrecedencePattern Between
```
Between "P" and "Q", it is always the case that if "R" holds, then "S" previously held
```

#### Countertraces
```
true;⌈(P && (!Q && !S))⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedencePattern_Between_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
|  | ![](../img/failure_paths/negative/PrecedencePattern_Between_0.svg) |


### PrecedencePattern AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then "S" previously held
```

#### Countertraces
```
true;⌈P⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedencePattern_AfterUntil_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
|  | ![](../img/failure_paths/negative/PrecedencePattern_AfterUntil_0.svg) |

