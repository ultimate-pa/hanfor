<!-- Auto generated file, do not make any changes here. -->

## PrecedencePattern

### PrecedencePattern Globally
```
Globally, it is always the case that if "R" holds, then "Q" previously held
```
```
Counterexample: ⌈!Q⌉;⌈R⌉;true
```
![](../img/patterns/PrecedencePattern_Globally.svg)
### PrecedencePattern Before
```
Before "Q", it is always the case that if "S" holds, then "R" previously held
```
```
Counterexample: ⌈(!Q && !R)⌉;⌈(!Q && S)⌉;true
```
![](../img/patterns/PrecedencePattern_Before.svg)
### PrecedencePattern After
```
After "Q", it is always the case that if "S" holds, then "R" previously held
```
```
Counterexample: true;⌈(Q && !R)⌉;⌈!R⌉;⌈S⌉;true
```
![](../img/patterns/PrecedencePattern_After.svg)
### PrecedencePattern Between
```
Between "Q" and "R", it is always the case that if "T" holds, then "S" previously held
```
```
Counterexample: true;⌈(Q && (!R && !S))⌉;⌈(!R && !S)⌉;⌈(!R && (!S && T))⌉;⌈!R⌉;⌈R⌉;true
```
![](../img/patterns/PrecedencePattern_Between.svg)
### PrecedencePattern AfterUntil
```
After "Q" until "R", it is always the case that if "T" holds, then "S" previously held
```
```
Counterexample: true;⌈(Q && (!R && !S))⌉;⌈(!R && !S)⌉;⌈(!R && T)⌉;true
```
![](../img/patterns/PrecedencePattern_AfterUntil.svg)
