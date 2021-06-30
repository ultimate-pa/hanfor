<!-- Auto generated file, do not make any changes here. -->

## BndDelayedResponsePatternTU

### BndDelayedResponsePatternTU Globally
```
Globally, it is always the case that if "R" holds for at least "5" time units, then "Q" holds after at most "10" time units
```

#### Countertraces
```
true;⌈R⌉ ∧ ℓ ≥ 5;⌈!Q⌉ ∧ ℓ > 10;true
```

#### Phase Event Automata
![](../img/patterns/BndDelayedResponsePatternTU_Globally_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/BndDelayedResponsePatternTU_Globally_0.svg) |  |
| ![](../img/failure_paths/positive/BndDelayedResponsePatternTU_Globally_1.svg) |  |
| ![](../img/failure_paths/positive/BndDelayedResponsePatternTU_Globally_2.svg) |  |
| ![](../img/failure_paths/positive/BndDelayedResponsePatternTU_Globally_3.svg) |  |
