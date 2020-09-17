<!-- Auto generated file, do not make any changes here. -->

## BndResponsePatternUT

### BndResponsePatternUT Globally
```
Globally, it is always the case that if "R" holds, then "Q" holds after at most "5" time units
```

#### Countertraces
```
true;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/BndResponsePatternUT_Globally_0.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/BndResponsePatternUT_Globally_0.svg) | ![](../img/failure_paths/negative/BndResponsePatternUT_Globally_0.svg) |
| ![](../img/failure_paths/positive/BndResponsePatternUT_Globally_1.svg) |  |


### BndResponsePatternUT Before
```
Before "Q", it is always the case that if "S" holds, then "R" holds after at most "5" time units
```

#### Countertraces
```
⌈!Q⌉;⌈(!Q && (!R && S))⌉;⌈(!Q && !R)⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/BndResponsePatternUT_Before_0.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndResponsePatternUT_Before_0.svg) |


### BndResponsePatternUT After
```
After "Q", it is always the case that if "S" holds, then "R" holds after at most "5" time units
```

#### Countertraces
```
true;⌈Q⌉;true;⌈(!R && S)⌉;⌈!R⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/BndResponsePatternUT_After_0.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/BndResponsePatternUT_After_0.svg) | ![](../img/failure_paths/negative/BndResponsePatternUT_After_0.svg) |
| ![](../img/failure_paths/positive/BndResponsePatternUT_After_1.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternUT_After_2.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternUT_After_3.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternUT_After_4.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternUT_After_5.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternUT_After_6.svg) |  |
| ![](../img/failure_paths/positive/BndResponsePatternUT_After_7.svg) |  |


### BndResponsePatternUT Between
```
Between "Q" and "R", it is always the case that if "T" holds, then "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && (!S && T))⌉;⌈(!R && !S)⌉ ∧ ℓ > 5;⌈!R⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndResponsePatternUT_Between_0.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndResponsePatternUT_Between_0.svg) |


### BndResponsePatternUT AfterUntil
```
After "Q" until "R", it is always the case that if "T" holds, then "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈Q⌉;⌈!R⌉;⌈(!R && (!S && T))⌉;⌈(!R && !S)⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/BndResponsePatternUT_AfterUntil_0.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndResponsePatternUT_AfterUntil_0.svg) |

