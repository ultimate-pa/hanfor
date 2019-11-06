<!-- Auto generated file, do not make any changes here. -->

## InstAbsPattern

### InstAbsPattern Globally
```
Globally, it is never the case that "Q" holds
```
```
Counterexample: true;⌈Q⌉;true
```
![](../img/patterns/InstAbsPattern_Globally.svg)
### InstAbsPattern After
```
After "Q", it is never the case that "R" holds
```
```
Counterexample: true;⌈Q⌉;true;⌈R⌉;true
```
![](../img/patterns/InstAbsPattern_After.svg)
### InstAbsPattern Between
```
Between "Q" and "R", it is never the case that "S" holds
```
```
Counterexample: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && S)⌉;⌈!R⌉;⌈R⌉;true
```
![](../img/patterns/InstAbsPattern_Between.svg)
### InstAbsPattern AfterUntil
```
After "Q" until "R", it is never the case that "S" holds
```
```
Counterexample: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && S)⌉;true
```
![](../img/patterns/InstAbsPattern_AfterUntil.svg)
