<!-- Auto generated file, do not make any changes here. -->

## MaxDurationPattern

### MaxDurationPattern Globally
```
Globally, it is always the case that once "Q" becomes satisfied, it holds for less than "5" time units
```

```
Countertraces: (true;⌈Q⌉ ∧ ℓ ≥ 5;true)
```

![](../img/patterns/MaxDurationPattern_Globally_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/MaxDurationPattern_Globally_0.svg) |


### MaxDurationPattern Before
```
Before "Q", it is always the case that once "R" becomes satisfied, it holds for less than "5" time units
```

```
Countertraces: (⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;true)
```

![](../img/patterns/MaxDurationPattern_Before_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/MaxDurationPattern_Before_0.svg) |


### MaxDurationPattern After
```
After "Q", it is always the case that once "R" becomes satisfied, it holds for less than "5" time units
```

```
Countertraces: (true;⌈Q⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ ≥ 5;true)
```

![](../img/patterns/MaxDurationPattern_After_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/MaxDurationPattern_After_0.svg) |


### MaxDurationPattern Between
```
Between "Q" and "R", it is always the case that once "S" becomes satisfied, it holds for less than "5" time units
```

```
Countertraces: (true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && S)⌉ ∧ ℓ ≥ 5;⌈!R⌉;⌈R⌉;true)
```

![](../img/patterns/MaxDurationPattern_Between_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/MaxDurationPattern_Between_0.svg) |


### MaxDurationPattern AfterUntil
```
After "Q" until "R", it is always the case that once "S" becomes satisfied, it holds for less than "5" time units
```

```
Countertraces: (true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && S)⌉ ∧ ℓ ≥ 5;true)
```

![](../img/patterns/MaxDurationPattern_AfterUntil_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/MaxDurationPattern_AfterUntil_0.svg) |

