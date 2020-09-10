<!-- Auto generated file, do not make any changes here. -->

## BndDelayedResponsePatternUT

### BndDelayedResponsePatternUT Globally
```
Globally, it is always the case that if "R" holds, then "Q" holds after at most "5" time units for at least "10" time units
```

```
Countertraces: (true;⌈R⌉;⌈!Q⌉ ∧ ℓ > 5;true), (true;⌈R⌉;⌈!Q⌉ ∧ ℓ ≤ 5;⌈Q⌉ ∧ ℓ < 10;⌈!Q⌉;true)
```

![](../img/patterns/BndDelayedResponsePatternUT_Globally_0.svg)

![](../img/patterns/BndDelayedResponsePatternUT_Globally_1.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/BndDelayedResponsePatternUT_Globally_0.svg) | ![](../img/failure_paths/negative/BndDelayedResponsePatternUT_Globally_0.svg) |
|  | ![](../img/failure_paths/negative/BndDelayedResponsePatternUT_Globally_1.svg) |

