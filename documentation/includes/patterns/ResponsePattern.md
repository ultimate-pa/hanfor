<!-- Auto generated file, do not make any changes here. -->

## ResponsePattern

### ResponsePattern Before
```
Before "P", it is always the case that if "R" holds, then "S" eventually holds
```

#### Countertraces
```
⌈!P⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉;⌈P⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponsePattern_Before_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
|  | ![](../img/failure_paths/negative/ResponsePattern_Before_0.svg) |


### ResponsePattern Between
```
Between "P" and "Q", it is always the case that if "R" holds, then "S" eventually holds
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponsePattern_Between_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
|  | ![](../img/failure_paths/negative/ResponsePattern_Between_0.svg) |


### ResponsePattern AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then "S" eventually holds
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponsePattern_AfterUntil_0.svg)

#### Examples


