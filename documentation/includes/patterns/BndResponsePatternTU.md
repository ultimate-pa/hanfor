<!-- Auto generated file, do not make any changes here. -->

## BndResponsePatternTU

### BndResponsePatternTU Globally
```
Globally, it is always the case that if "R" holds for at least "5" time units, then "Q" holds afterwards
```

#### Countertraces
```
true;⌈R⌉ ∧ ℓ ≥ 5;⌈!Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndResponsePatternTU_Globally_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Globally_0.svg) | ![](../img/failure_paths/negative/BndResponsePatternTU_Globally_0.svg) |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Globally_1.svg) | ![](../img/failure_paths/negative/BndResponsePatternTU_Globally_1.svg) |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Globally_2.svg) |  |


### BndResponsePatternTU Before
```
Before "Q", it is always the case that if "S" holds for at least "5" time units, then "R" holds afterwards
```

#### Countertraces
```
⌈!Q⌉;⌈(!Q && S)⌉ ∧ ℓ ≥ 5;⌈(!Q && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndResponsePatternTU_Before_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Before_0.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Before_1.svg) |  |


### BndResponsePatternTU After
```
After "Q", it is always the case that if "S" holds for at least "5" time units, then "R" holds afterwards
```

#### Countertraces
```
true;⌈Q⌉;true;⌈S⌉ ∧ ℓ ≥ 5;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndResponsePatternTU_After_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/BndResponsePatternTU_After_0.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_After_1.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_After_2.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_After_3.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_After_4.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_After_5.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_After_6.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_After_7.svg) |  |


### BndResponsePatternTU Between
```
Between "Q" and "R", it is always the case that if "T" holds for at least "5" time units, then "S" holds afterwards
```

#### Countertraces
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && T)⌉ ∧ ℓ ≥ 5;⌈(!R && !S)⌉;⌈!R⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndResponsePatternTU_Between_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Between_0.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Between_1.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Between_2.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Between_3.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Between_4.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Between_5.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Between_6.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Between_7.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Between_8.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Between_9.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Between_10.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_Between_11.svg) |  |


### BndResponsePatternTU AfterUntil
```
After "Q" until "R", it is always the case that if "T" holds for at least "5" time units, then "S" holds afterwards
```

#### Countertraces
```
true;⌈Q⌉;⌈!R⌉;⌈(!R && T)⌉ ∧ ℓ ≥ 5;⌈(!R && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndResponsePatternTU_AfterUntil_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/BndResponsePatternTU_AfterUntil_0.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_AfterUntil_1.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_AfterUntil_2.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternTU_AfterUntil_3.svg) |  |

