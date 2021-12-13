<!-- Auto generated file, do not make any changes here. -->

## UniversalityPattern

### UniversalityPattern Globally
```
Globally, it is always the case that "R" holds
```

#### Countertraces
```
true;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityPattern_Globally_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
|  | ![](../img/failure_paths/negative/UniversalityPattern_Globally_0.svg) |
|  | ![](../img/failure_paths/negative/UniversalityPattern_Globally_1.svg) |


### UniversalityPattern Before
```
Before "P", it is always the case that "R" holds
```

#### Countertraces
```
⌈!P⌉;⌈(!P && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityPattern_Before_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
|  | ![](../img/failure_paths/negative/UniversalityPattern_Before_0.svg) |


### UniversalityPattern After
```
After "P", it is always the case that "R" holds
```

#### Countertraces
```
true;⌈P⌉;true;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityPattern_After_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
|  | ![](../img/failure_paths/negative/UniversalityPattern_After_0.svg) |


### UniversalityPattern Between
```
Between "P" and "Q", it is always the case that "R" holds
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityPattern_Between_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
|  | ![](../img/failure_paths/negative/UniversalityPattern_Between_0.svg) |


### UniversalityPattern AfterUntil
```
After "P" until "Q", it is always the case that "R" holds
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityPattern_AfterUntil_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
|  | ![](../img/failure_paths/negative/UniversalityPattern_AfterUntil_0.svg) |

