<!-- Auto generated file, do not make any changes here. -->

## TogglePatternDelayed

### TogglePatternDelayed Globally
```
Globally, it is always the case that if "Q" holds then "R" toggles "S" at most "5" time units later
```
```
Countertraces: true;⌈(Q && R)⌉;⌈!R⌉ ∧ ℓ ≥ 5;⌈(!R && !S)⌉;true
```

![](../img/patterns/TogglePatternDelayed_Globally.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/TogglePatternDelayed_Globally_0.svg) |  |

