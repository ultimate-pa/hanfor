<!-- Auto generated file, do not make any changes here. -->

## BndResponsePatternTT

### BndResponsePatternTT Globally
```
Globally, it is always the case that if "R" holds for at least "5" time units, then "Q" holds afterwards for at least "10" time units
```

#### Countertraces
```
true;⌈R⌉ ∧ ℓ ≥ 5;⌈Q⌉ ∧ ℓ <₀ 10;⌈!Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/BndResponsePatternTT_Globally_0.svg)

#### Examples
| Positive Example { .positive-example} | Negative Example { .negative-example} |
| :---: | :---: |
| ![](../img/failure_paths/positive/BndResponsePatternTT_Globally_0.svg) | ![](../img/failure_paths/negative/BndResponsePatternTT_Globally_0.svg) |
| ![](../img/failure_paths/positive/BndResponsePatternTT_Globally_1.svg) | ![](../img/failure_paths/negative/BndResponsePatternTT_Globally_1.svg) |
| ![](../img/failure_paths/positive/BndResponsePatternTT_Globally_2.svg) |  |

