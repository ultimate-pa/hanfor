<!-- Auto generated file, do not make any changes here. -->

## UniversalityPattern

### UniversalityPattern Globally
```
Globally, it is always the case that "Q" holds
```
```
Counterexample: true;⌈!Q⌉;true
```

![](../img/patterns/UniversalityPattern_Globally.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
| ![](../img/failure_paths/UniversalityPattern_Globally_0.svg) | |


### UniversalityPattern Before
```
Before "Q", it is always the case that "R" holds
```
```
Counterexample: ⌈!Q⌉;⌈(!Q && !R)⌉;true
```

![](../img/patterns/UniversalityPattern_Before.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
| ![](../img/failure_paths/UniversalityPattern_Before_0.svg) | |


### UniversalityPattern After
```
After "Q", it is always the case that "R" holds
```
```
Counterexample: true;⌈Q⌉;true;⌈!R⌉;true
```

![](../img/patterns/UniversalityPattern_After.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
| ![](../img/failure_paths/UniversalityPattern_After_0.svg) | |


### UniversalityPattern Between
```
Between "Q" and "R", it is always the case that "S" holds
```
```
Counterexample: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !S)⌉;⌈!R⌉;⌈R⌉;true
```

![](../img/patterns/UniversalityPattern_Between.svg)


### UniversalityPattern AfterUntil
```
After "Q" until "R", it is always the case that "S" holds
```
```
Counterexample: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !S)⌉;true
```

![](../img/patterns/UniversalityPattern_AfterUntil.svg)

<div class="pattern-examples"></div>
| Positive example | Negative example |
| --- | --- |
| ![](../img/failure_paths/UniversalityPattern_AfterUntil_0.svg) | |

