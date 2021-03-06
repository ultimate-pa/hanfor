<!-- Auto generated file, do not make any changes here. -->

## UniversalityPatternDelayed

### UniversalityPatternDelayed Globally
```
Globally, it is always the case that "Q" holds after at most "5" time units
```

#### Countertraces
```
⌈true⌉ ∧ ℓ ≥ 5;⌈!Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityPatternDelayed_Globally_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/UniversalityPatternDelayed_Globally_0.svg) |  |
| ![](../img/failure_paths/positive/UniversalityPatternDelayed_Globally_1.svg) |  |


### UniversalityPatternDelayed Before
```
Before "Q", it is always the case that "R" holds after at most "5" time units
```

#### Countertraces
```
⌈!Q⌉ ∧ ℓ ≥ 5;⌈(!Q && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityPatternDelayed_Before_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/UniversalityPatternDelayed_Before_0.svg) |  |
| ![](../img/failure_paths/positive/UniversalityPatternDelayed_Before_1.svg) |  |


### UniversalityPatternDelayed After
```
After "Q", it is always the case that "R" holds after at most "5" time units
```

#### Countertraces
```
true;⌈Q⌉;⌈true⌉ ∧ ℓ ≥ 5;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityPatternDelayed_After_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/UniversalityPatternDelayed_After_0.svg) |  |
| ![](../img/failure_paths/positive/UniversalityPatternDelayed_After_1.svg) |  |


### UniversalityPatternDelayed Between
```
Between "Q" and "R", it is always the case that "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈(Q && !R)⌉;⌈!R⌉ ∧ ℓ ≥ 5;⌈(!R && !S)⌉;true;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityPatternDelayed_Between_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/UniversalityPatternDelayed_Between_0.svg) |  |
| ![](../img/failure_paths/positive/UniversalityPatternDelayed_Between_1.svg) |  |
| ![](../img/failure_paths/positive/UniversalityPatternDelayed_Between_2.svg) |  |
| ![](../img/failure_paths/positive/UniversalityPatternDelayed_Between_3.svg) |  |


### UniversalityPatternDelayed AfterUntil
```
After "Q" until "R", it is always the case that "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈Q⌉;⌈!R⌉ ∧ ℓ ≥ 5;⌈(!R && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityPatternDelayed_AfterUntil_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/UniversalityPatternDelayed_AfterUntil_0.svg) |  |
| ![](../img/failure_paths/positive/UniversalityPatternDelayed_AfterUntil_1.svg) |  |
| ![](../img/failure_paths/positive/UniversalityPatternDelayed_AfterUntil_2.svg) |  |
| ![](../img/failure_paths/positive/UniversalityPatternDelayed_AfterUntil_3.svg) |  |

