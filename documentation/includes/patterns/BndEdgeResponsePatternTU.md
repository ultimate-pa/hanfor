<!-- Auto generated file, do not make any changes here. -->

## BndEdgeResponsePatternTU

### BndEdgeResponsePatternTU Globally
```
Globally, it is always the case that once "R" becomes satisfied and holds for at most "5" time units, then "Q" holds afterwards
```

#### Countertraces
```
true;⌈!R⌉;⌈R⌉ ∧ ℓ ≤ 5;⌈(!Q && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEdgeResponsePatternTU_Globally_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternTU_Globally_0.svg) |  |


### BndEdgeResponsePatternTU Before
```
Before "Q", it is always the case that once "S" becomes satisfied and holds for at most "5" time units, then "R" holds afterwards
```

#### Countertraces
```
⌈!Q⌉;⌈(!Q && !S)⌉;⌈(!Q && S)⌉ ∧ ℓ ≥ 5;⌈(!Q && (!R && !S))⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEdgeResponsePatternTU_Before_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternTU_Before_0.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternTU_Before_1.svg) |  |


### BndEdgeResponsePatternTU After
```
After "Q", it is always the case that once "S" becomes satisfied and holds for at most "5" time units, then "R" holds afterwards
```

#### Countertraces
```
true;⌈Q⌉;true;⌈!S⌉;⌈S⌉ ∧ ℓ ≤ 5;⌈(!R && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEdgeResponsePatternTU_After_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternTU_After_0.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternTU_After_1.svg) |  |


### BndEdgeResponsePatternTU Between
```
Between "Q" and "R", it is always the case that once "T" becomes satisfied and holds for at most "5" time units, then "S" holds afterwards
```

#### Countertraces
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !T)⌉;⌈(!R && T)⌉ ∧ ℓ ≤ 5;⌈(!R && (!S && !T))⌉;⌈!R⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEdgeResponsePatternTU_Between_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternTU_Between_0.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternTU_Between_1.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternTU_Between_2.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternTU_Between_3.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternTU_Between_4.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternTU_Between_5.svg) |  |


### BndEdgeResponsePatternTU AfterUntil
```
After "Q" until "R", it is always the case that once "T" becomes satisfied and holds for at most "5" time units, then "S" holds afterwards
```

#### Countertraces
```
true;⌈Q⌉;⌈!R⌉;⌈(!R && !T)⌉;⌈(!R && T)⌉ ∧ ℓ ≤ 5;⌈(!R && (!S && !T))⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEdgeResponsePatternTU_AfterUntil_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternTU_AfterUntil_0.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternTU_AfterUntil_1.svg) |  |

