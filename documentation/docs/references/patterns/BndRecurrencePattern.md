<!-- Auto generated file, do not make any changes here. -->

## BndRecurrencePattern

### BndRecurrencePattern Globally
```
Globally, it is always the case that "Q" holds at least every "5" time units
```

```
Countertraces: (true;⌈!Q⌉ ∧ ℓ > 5;true)
```

![](../img/patterns/BndRecurrencePattern_Globally_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndRecurrencePattern_Globally_0.svg) |


### BndRecurrencePattern Before
```
Before "Q", it is always the case that "R" holds at least every "5" time units
```

```
Countertraces: (⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > 5;true)
```

![](../img/patterns/BndRecurrencePattern_Before_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndRecurrencePattern_Before_0.svg) |


### BndRecurrencePattern After
```
After "Q", it is always the case that "R" holds at least every "5" time units
```

```
Countertraces: (true;⌈Q⌉;true;⌈!R⌉ ∧ ℓ > 5;true)
```

![](../img/patterns/BndRecurrencePattern_After_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndRecurrencePattern_After_0.svg) |


### BndRecurrencePattern Between
```
Between "Q" and "R", it is always the case that "S" holds at least every "5" time units
```

```
Countertraces: (true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !S)⌉ ∧ ℓ > 5;⌈!R⌉;⌈R⌉;true)
```

![](../img/patterns/BndRecurrencePattern_Between_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndRecurrencePattern_Between_0.svg) |


### BndRecurrencePattern AfterUntil
```
After "Q" until "R", it is always the case that "S" holds at least every "5" time units
```

```
Countertraces: (true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !S)⌉ ∧ ℓ > 5;true)
```

![](../img/patterns/BndRecurrencePattern_AfterUntil_0.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/BndRecurrencePattern_AfterUntil_0.svg) |

