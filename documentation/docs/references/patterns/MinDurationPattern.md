<!-- Auto generated file, do not make any changes here. -->

## MinDurationPattern

### MinDurationPattern Globally
```
Globally, it is always the case that once "Q" becomes satisfied, it holds for at least "5" time units
```

#### Countertraces
```
true;⌈!Q⌉;⌈Q⌉ ∧ ℓ < 5;⌈!Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/MinDurationPattern_Globally_0.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/MinDurationPattern_Globally_0.svg) |


### MinDurationPattern Before
```
Before "Q", it is always the case that once "R" becomes satisfied, it holds for at least "5" time units
```

#### Countertraces
```
⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < 5;⌈(!Q && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/MinDurationPattern_Before_0.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/MinDurationPattern_Before_0.svg) |


### MinDurationPattern After
```
After "Q", it is always the case that once "R" becomes satisfied, it holds for at least "5" time units
```

#### Countertraces
```
true;⌈Q⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ < 5;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/MinDurationPattern_After_0.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/MinDurationPattern_After_0.svg) |


### MinDurationPattern Between
```
Between "Q" and "R", it is always the case that once "S" becomes satisfied, it holds for at least "5" time units
```

#### Countertraces
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !S)⌉;⌈(!R && S)⌉ ∧ ℓ < 5;⌈(!R && !S)⌉;⌈!R⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/MinDurationPattern_Between_0.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/MinDurationPattern_Between_0.svg) |


### MinDurationPattern AfterUntil
```
After "Q" until "R", it is always the case that once "S" becomes satisfied, it holds for at least "5" time units
```

#### Countertraces
```
true;⌈Q⌉;⌈!R⌉;⌈(!R && !S)⌉;⌈(!R && S)⌉ ∧ ℓ < 5;⌈(!R && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/MinDurationPattern_AfterUntil_0.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/MinDurationPattern_AfterUntil_0.svg) |

