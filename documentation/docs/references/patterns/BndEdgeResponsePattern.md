<!-- Auto generated file, do not make any changes here. -->

## BndEdgeResponsePattern

### BndEdgeResponsePattern Globally
```
Globally, it is always the case that once "R" becomes satisfied, "Q" holds for at least "5" time units
```

#### Countertraces
```
true;⌈!R⌉;⌈R⌉;⌈Q⌉ ∧ ℓ < 5;⌈!Q⌉;true
true;⌈!R⌉;⌈(!Q && R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndEdgeResponsePattern_Globally_0.svg)
![](../img/patterns/BndEdgeResponsePattern_Globally_1.svg)

#### Examples

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_Globally_0.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_Globally_1.svg) |  |
| ![](../img/failure_paths/positive/BndEdgeResponsePattern_Globally_2.svg) |  |

