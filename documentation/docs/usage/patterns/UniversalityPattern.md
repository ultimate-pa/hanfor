<!-- Auto generated file, do not make any changes here. -->

## UniversalityPattern

### UniversalityPattern Globally
```
Globally, it is always the case that "Q" holds
```
```
true;⌈!Q⌉;true
```
![](../img/patterns/UniversalityPattern_Globally.svg)
### UniversalityPattern Before
```
Before "Q", it is always the case that "R" holds
```
```
⌈!Q⌉;⌈(!Q && !R)⌉;true
```
![](../img/patterns/UniversalityPattern_Before.svg)
### UniversalityPattern After
```
After "Q", it is always the case that "R" holds
```
```
true;⌈Q⌉;true;⌈!R⌉;true
```
![](../img/patterns/UniversalityPattern_After.svg)
### UniversalityPattern Between
```
Between "Q" and "R", it is always the case that "S" holds
```
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !S)⌉;⌈!R⌉;⌈R⌉;true
```
![](../img/patterns/UniversalityPattern_Between.svg)
### UniversalityPattern AfterUntil
```
After "Q" until "R", it is always the case that "S" holds
```
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !S)⌉;true
```
![](../img/patterns/UniversalityPattern_AfterUntil.svg)
