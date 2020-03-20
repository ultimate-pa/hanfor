<!-- Auto generated file, do not make any changes here. -->

## InstAbsPattern

### InstAbsPattern Globally
```
Globally, it is never the case that "Q" holds
```
```
Countertraces: true;⌈Q⌉;true
```

![](../img/patterns/InstAbsPattern_Globally.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/InstAbsPattern_Globally_0.svg) |
|  | ![](../img/failure_paths/negative/InstAbsPattern_Globally_1.svg) |


### InstAbsPattern After
```
After "Q", it is never the case that "R" holds
```
```
Countertraces: true;⌈Q⌉;true;⌈R⌉;true
```

![](../img/patterns/InstAbsPattern_After.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/InstAbsPattern_After_0.svg) |
|  | ![](../img/failure_paths/negative/InstAbsPattern_After_1.svg) |


### InstAbsPattern Between
```
Between "Q" and "R", it is never the case that "S" holds
```
```
Countertraces: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && S)⌉;⌈!R⌉;⌈R⌉;true
```

![](../img/patterns/InstAbsPattern_Between.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/InstAbsPattern_Between_0.svg) | ![](../img/failure_paths/negative/InstAbsPattern_Between_0.svg) |
| ![](../img/failure_paths/positive/InstAbsPattern_Between_1.svg) |  |


### InstAbsPattern AfterUntil
```
After "Q" until "R", it is never the case that "S" holds
```
```
Countertraces: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && S)⌉;true
```

![](../img/patterns/InstAbsPattern_AfterUntil.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/InstAbsPattern_AfterUntil_0.svg) |

