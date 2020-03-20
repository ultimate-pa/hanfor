<!-- Auto generated file, do not make any changes here. -->

## ResponseChain21Pattern

### ResponseChain21Pattern Before
```
Before "Q", it is always the case that if "U" holds and is succeeded by "T", then "S" eventually holds after "R"
```
```
Countertraces: ⌈!Q⌉;⌈(!Q && U)⌉;⌈!Q⌉;⌈(!Q && T)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉;⌈!Q⌉;⌈Q⌉;true
```

![](../img/patterns/ResponseChain21Pattern_Before.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/ResponseChain21Pattern_Before_0.svg) | ![](../img/failure_paths/negative/ResponseChain21Pattern_Before_0.svg) |
| ![](../img/failure_paths/positive/ResponseChain21Pattern_Before_1.svg) |  |
| ![](../img/failure_paths/positive/ResponseChain21Pattern_Before_2.svg) |  |
| ![](../img/failure_paths/positive/ResponseChain21Pattern_Before_3.svg) |  |
| ![](../img/failure_paths/positive/ResponseChain21Pattern_Before_4.svg) |  |
| ![](../img/failure_paths/positive/ResponseChain21Pattern_Before_5.svg) |  |
| ![](../img/failure_paths/positive/ResponseChain21Pattern_Before_6.svg) |  |
| ![](../img/failure_paths/positive/ResponseChain21Pattern_Before_7.svg) |  |


### ResponseChain21Pattern Between
```
Between "Q" and "R", it is always the case that if "V" holds and is succeeded by "U", then "T" eventually holds after "S"
```
```
Countertraces: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && V)⌉;⌈!R⌉;⌈(!R && U)⌉;⌈!R⌉;⌈(!R && S)⌉;⌈(!R && !T)⌉;⌈R⌉;true
```

![](../img/patterns/ResponseChain21Pattern_Between.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/ResponseChain21Pattern_Between_0.svg) |

