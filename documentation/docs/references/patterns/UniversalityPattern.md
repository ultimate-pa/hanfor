<!-- Auto generated file, do not make any changes here. -->

## UniversalityPattern

### UniversalityPattern Globally
```
Globally, it is always the case that "Q" holds
```
```
Countertraces: true;⌈!Q⌉;true
```

![](../img/patterns/UniversalityPattern_Globally.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/UniversalityPattern_Globally_0.svg) | ![](../img/failure_paths/negative/UniversalityPattern_Globally_0.svg) |
|  | ![](../img/failure_paths/negative/UniversalityPattern_Globally_1.svg) |


### UniversalityPattern Before
```
Before "Q", it is always the case that "R" holds
```
```
Countertraces: ⌈!Q⌉;⌈(!Q && !R)⌉;true
```

![](../img/patterns/UniversalityPattern_Before.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/UniversalityPattern_Before_0.svg) | ![](../img/failure_paths/negative/UniversalityPattern_Before_0.svg) |


### UniversalityPattern After
```
After "Q", it is always the case that "R" holds
```
```
Countertraces: true;⌈Q⌉;true;⌈!R⌉;true
```

![](../img/patterns/UniversalityPattern_After.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/UniversalityPattern_After_0.svg) | ![](../img/failure_paths/negative/UniversalityPattern_After_0.svg) |
| ![](../img/failure_paths/positive/UniversalityPattern_After_1.svg) |  |


### UniversalityPattern Between
```
Between "Q" and "R", it is always the case that "S" holds
```
```
Countertraces: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !S)⌉;⌈!R⌉;⌈R⌉;true
```

![](../img/patterns/UniversalityPattern_Between.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
|  | ![](../img/failure_paths/negative/UniversalityPattern_Between_0.svg) |


### UniversalityPattern AfterUntil
```
After "Q" until "R", it is always the case that "S" holds
```
```
Countertraces: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !S)⌉;true
```

![](../img/patterns/UniversalityPattern_AfterUntil.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/UniversalityPattern_AfterUntil_0.svg) | ![](../img/failure_paths/negative/UniversalityPattern_AfterUntil_0.svg) |
| ![](../img/failure_paths/positive/UniversalityPattern_AfterUntil_1.svg) |  |

