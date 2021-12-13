<!-- Auto generated file, do not make any changes here. -->

## AbsencePattern

### AbsencePattern Globally
```
Globally, it is never the case that "R" holds
```

#### Countertraces
```
true;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/AbsencePattern_Globally_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/AbsencePattern_Globally_0.svg) |  |


### AbsencePattern Before
```
Before "P", it is never the case that "R" holds
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/AbsencePattern_Before_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/AbsencePattern_Before_0.svg) |  |


### AbsencePattern After
```
After "P", it is never the case that "R" holds
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/AbsencePattern_After_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/AbsencePattern_After_0.svg) |  |
| ![](../img/failure_paths/positive/AbsencePattern_After_1.svg) |  |


### AbsencePattern Between
```
Between "P" and "Q", it is never the case that "R" holds
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/AbsencePattern_Between_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/AbsencePattern_Between_0.svg) |  |
| ![](../img/failure_paths/positive/AbsencePattern_Between_1.svg) |  |
| ![](../img/failure_paths/positive/AbsencePattern_Between_2.svg) |  |
| ![](../img/failure_paths/positive/AbsencePattern_Between_3.svg) |  |


### AbsencePattern AfterUntil
```
After "P" until "Q", it is never the case that "R" holds
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/AbsencePattern_AfterUntil_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/AbsencePattern_AfterUntil_0.svg) |  |
| ![](../img/failure_paths/positive/AbsencePattern_AfterUntil_1.svg) |  |

