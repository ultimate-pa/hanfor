<!-- Auto generated file, do not make any changes here. -->

## EdgeResponseDelayPattern

### EdgeResponseDelayPattern Globally
```
Globally, it is always the case that once "R" becomes satisfied, "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseDelayPattern_Globally_0.svg)

#### Examples



### EdgeResponseDelayPattern Before
```
Before "P", it is always the case that once "R" becomes satisfied, "S" holds after at most "5" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseDelayPattern_Before_0.svg)

#### Examples



### EdgeResponseDelayPattern After
```
After "P", it is always the case that once "R" becomes satisfied, "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseDelayPattern_After_0.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_0.svg) |  |
| ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_1.svg) |  |
| ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_2.svg) |  |
| ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_3.svg) |  |
| ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_4.svg) |  |
| ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_5.svg) |  |
| ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_6.svg) |  |
| ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_7.svg) |  |
| ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_8.svg) |  |
| ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_9.svg) |  |
| ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_10.svg) |  |
| ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_11.svg) |  |
| ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_12.svg) |  |
| ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_13.svg) |  |
| ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_14.svg) |  |
| ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_15.svg) |  |


### EdgeResponseDelayPattern Between
```
Between "P" and "Q", it is always the case that once "R" becomes satisfied, "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > 5;true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseDelayPattern_Between_0.svg)

#### Examples



### EdgeResponseDelayPattern AfterUntil
```
After "P" until "Q", it is always the case that once "R" becomes satisfied, "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseDelayPattern_AfterUntil_0.svg)

#### Examples


