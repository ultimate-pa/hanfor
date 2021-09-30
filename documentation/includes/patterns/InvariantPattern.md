<!-- Auto generated file, do not make any changes here. -->

## InvariantPattern

### InvariantPattern Globally
```
Globally, it is always the case that if "R" holds, then "Q" holds as well
```

#### Countertraces
```
true;⌈(!Q && R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvariantPattern_Globally_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/InvariantPattern_Globally_0.svg) | ![](../img/failure_paths/negative/InvariantPattern_Globally_0.svg) |


### InvariantPattern Before
```
Before "Q", it is always the case that if "S" holds, then "R" holds as well
```

#### Countertraces
```
⌈!Q⌉;⌈(!Q && (!R && S))⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvariantPattern_Before_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/InvariantPattern_Before_0.svg) | ![](../img/failure_paths/negative/InvariantPattern_Before_0.svg) |


### InvariantPattern After
```
After "Q", it is always the case that if "S" holds, then "R" holds as well
```

#### Countertraces
```
true;⌈Q⌉;true;⌈(!R && S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvariantPattern_After_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/InvariantPattern_After_0.svg) | ![](../img/failure_paths/negative/InvariantPattern_After_0.svg) |
| ![](../img/failure_paths/positive/InvariantPattern_After_1.svg) |  |


### InvariantPattern Between
```
Between "Q" and "R", it is always the case that if "T" holds, then "S" holds as well
```

#### Countertraces
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && (!S && T))⌉;⌈!R⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvariantPattern_Between_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/InvariantPattern_Between_0.svg) | ![](../img/failure_paths/negative/InvariantPattern_Between_0.svg) |
| ![](../img/failure_paths/positive/InvariantPattern_Between_1.svg) |  |
| ![](../img/failure_paths/positive/InvariantPattern_Between_2.svg) |  |
| ![](../img/failure_paths/positive/InvariantPattern_Between_3.svg) |  |


### InvariantPattern AfterUntil
```
After "Q" until "R", it is always the case that if "T" holds, then "S" holds as well
```

#### Countertraces
```
true;⌈Q⌉;⌈!R⌉;⌈(!R && (!S && T))⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvariantPattern_AfterUntil_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/InvariantPattern_AfterUntil_0.svg) | ![](../img/failure_paths/negative/InvariantPattern_AfterUntil_0.svg) |
| ![](../img/failure_paths/positive/InvariantPattern_AfterUntil_1.svg) |  |

