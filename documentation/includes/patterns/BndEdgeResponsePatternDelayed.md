<!-- Auto generated file, do not make any changes here. -->

## BndEdgeResponsePatternDelayed

### BndEdgeResponsePatternDelayed Globally
```
Globally, it is always the case that once "R" becomes satisfied, "Q" holds after at most "5" time units for at least "10" time units
```

#### Countertraces
```
true;⌈!R⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ > 5;true
true;⌈!R⌉;⌈R⌉;⌈true⌉ ∧ ℓ < 5;⌈Q⌉ ∧ ℓ < 10;⌈!Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEdgeResponsePatternDelayed_Globally_0.svg)
![](../img/patterns/BndEdgeResponsePatternDelayed_Globally_1.svg)

#### Examples

| Positive Example { .negative-example } | Negative Example { .positive-example } |
| --- | --- |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternDelayed_Globally_0.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternDelayed_Globally_1.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternDelayed_Globally_2.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternDelayed_Globally_3.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternDelayed_Globally_4.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePatternDelayed_Globally_5.svg) |  |

