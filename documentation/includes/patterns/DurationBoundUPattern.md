<!-- Auto generated file, do not make any changes here. -->

## DurationBoundUPattern

### DurationBoundUPattern Globally
```
Globally, it is always the case that once "R" becomes satisfied, it holds for less than "5" time units
```

#### Countertraces
```
true;⌈R⌉ ∧ ℓ ≥ 5;true
```

#### Phase Event Automata
![](../img/patterns/DurationBoundUPattern_Globally_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/DurationBoundUPattern_Globally_0.svg) |  |


### DurationBoundUPattern Before
```
Before "P", it is always the case that once "R" becomes satisfied, it holds for less than "5" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ 5;true
```

#### Phase Event Automata
![](../img/patterns/DurationBoundUPattern_Before_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/DurationBoundUPattern_Before_0.svg) |  |


### DurationBoundUPattern After
```
After "P", it is always the case that once "R" becomes satisfied, it holds for less than "5" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ 5;true
```

#### Phase Event Automata
![](../img/patterns/DurationBoundUPattern_After_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/DurationBoundUPattern_After_0.svg) |  |
| ![](../img/failure_paths/positive/DurationBoundUPattern_After_1.svg) |  |


### DurationBoundUPattern Between
```
Between "P" and "Q", it is always the case that once "R" becomes satisfied, it holds for less than "5" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/DurationBoundUPattern_Between_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/DurationBoundUPattern_Between_0.svg) |  |
| ![](../img/failure_paths/positive/DurationBoundUPattern_Between_1.svg) |  |
| ![](../img/failure_paths/positive/DurationBoundUPattern_Between_2.svg) |  |
| ![](../img/failure_paths/positive/DurationBoundUPattern_Between_3.svg) |  |
| ![](../img/failure_paths/positive/DurationBoundUPattern_Between_4.svg) |  |
| ![](../img/failure_paths/positive/DurationBoundUPattern_Between_5.svg) |  |


### DurationBoundUPattern AfterUntil
```
After "P" until "Q", it is always the case that once "R" becomes satisfied, it holds for less than "5" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;true
```

#### Phase Event Automata
![](../img/patterns/DurationBoundUPattern_AfterUntil_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/DurationBoundUPattern_AfterUntil_0.svg) |  |
| ![](../img/failure_paths/positive/DurationBoundUPattern_AfterUntil_1.svg) |  |

