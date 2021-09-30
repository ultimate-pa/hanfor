<!-- Auto generated file, do not make any changes here. -->

## BndEdgeResponsePattern

### BndEdgeResponsePattern Globally
```
Globally, it is always the case that once "R" becomes satisfied, "Q" holds for at least "5" time units
```

#### Countertraces
```
true;⌈!R⌉;⌈R⌉;⌈Q⌉ ∧ ℓ < 5;⌈!Q⌉;true
true;⌈!R⌉;⌈(!Q && R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEdgeResponsePattern_Globally_0.svg)
![](../img/patterns/BndEdgeResponsePattern_Globally_1.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_Globally_0.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_Globally_1.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_Globally_2.svg) |  |


### BndEdgeResponsePattern Before
```
Before "Q", it is always the case that once "S" becomes satisfied, "R" holds for at least "5" time units
```

#### Countertraces
```
⌈!Q⌉;⌈(!Q && !S)⌉;⌈(!Q && S)⌉;⌈(!R || !Q)⌉ ∧ ℓ < 5;⌈(!Q && !R)⌉;true
⌈!Q⌉;⌈(!Q && !S)⌉;⌈(!Q && (!R && S))⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEdgeResponsePattern_Before_0.svg)
![](../img/patterns/BndEdgeResponsePattern_Before_1.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_Before_0.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_Before_1.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_Before_2.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_Before_3.svg) |  |


### BndEdgeResponsePattern After
```
After "Q", it is always the case that once "S" becomes satisfied, "R" holds for at least "5" time units
```

#### Countertraces
```
true;⌈Q⌉;true;⌈!S⌉;⌈S⌉;⌈R⌉ ∧ ℓ < 5;⌈!R⌉;true
true;⌈Q⌉;true;⌈!S⌉;⌈(!R && S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEdgeResponsePattern_After_0.svg)
![](../img/patterns/BndEdgeResponsePattern_After_1.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_After_0.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_After_1.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_After_2.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_After_3.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_After_4.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_After_5.svg) |  |


### BndEdgeResponsePattern Between
```
Between "Q" and "R", it is always the case that once "T" becomes satisfied, "S" holds for at least "5" time units
```

#### Countertraces
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(T || !R)⌉;⌈(!R && T)⌉;⌈(!R && S)⌉ ∧ ℓ < 5;⌈(!R && !S)⌉;⌈!R⌉;⌈R⌉;true
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !T)⌉;⌈(!R && (!S && T))⌉;⌈!R⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEdgeResponsePattern_Between_0.svg)
![](../img/patterns/BndEdgeResponsePattern_Between_1.svg)

#### Examples



### BndEdgeResponsePattern AfterUntil
```
After "Q" until "R", it is always the case that once "T" becomes satisfied, "S" holds for at least "5" time units
```

#### Countertraces
```
true;⌈Q⌉;⌈!R⌉;⌈(T || !R)⌉;⌈(!R && T)⌉;⌈(!R && S)⌉ ∧ ℓ < 5;⌈(!R && !S)⌉;true
true;⌈Q⌉;⌈!R⌉;⌈(!R && !T)⌉;⌈(!R && (!S && T))⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEdgeResponsePattern_AfterUntil_0.svg)
![](../img/patterns/BndEdgeResponsePattern_AfterUntil_1.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_AfterUntil_0.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_AfterUntil_1.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_AfterUntil_2.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_AfterUntil_3.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_AfterUntil_4.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_AfterUntil_5.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_AfterUntil_6.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_AfterUntil_7.svg) |  |

