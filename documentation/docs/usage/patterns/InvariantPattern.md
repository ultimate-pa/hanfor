<!-- Auto generated file, do not make any changes here. -->

## InvariantPattern

### InvariantPattern Globally
```
Globally, it is always the case that if "R" holds, then "Q" holds as well
```
```
true;⌈(!Q && R)⌉;true
```
![](../../img/patterns/InvariantPattern_Globally.svg)
### InvariantPattern Before
```
Before "Q", it is always the case that if "S" holds, then "R" holds as well
```
```
⌈!Q⌉;⌈(!Q && (!R && S))⌉;⌈!Q⌉;true
```
![](../../img/patterns/InvariantPattern_Before.svg)
### InvariantPattern After
```
After "Q", it is always the case that if "S" holds, then "R" holds as well
```
```
true;⌈Q⌉;true;⌈(!R && S)⌉;true
```
![](../../img/patterns/InvariantPattern_After.svg)
### InvariantPattern Between
```
Between "Q" and "R", it is always the case that if "T" holds, then "S" holds as well
```
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && (!S && T))⌉;⌈!R⌉;⌈R⌉;true
```
![](../../img/patterns/InvariantPattern_Between.svg)
### InvariantPattern AfterUntil
```
After "Q" until "R", it is always the case that if "T" holds, then "S" holds as well
```
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && (!S && T))⌉;true
```
![](../../img/patterns/InvariantPattern_AfterUntil.svg)
