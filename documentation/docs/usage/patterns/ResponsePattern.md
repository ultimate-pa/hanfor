<!-- Auto generated file, do not make any changes here. -->

## ResponsePattern

### ResponsePattern Globally
```
Globally, it is always the case that if "R" holds, then "Q" eventually holds
```
```
true;⌈(!Q && R)⌉;⌈!Q⌉;true
```
![](../../img/patterns/ResponsePattern_Globally.svg)
### ResponsePattern Before
```
Before "Q", it is always the case that if "S" holds, then "R" eventually holds
```
```
⌈!Q⌉;⌈(!Q && (!R && S))⌉;⌈(!Q && !R)⌉;⌈Q⌉;true
```
![](../../img/patterns/ResponsePattern_Before.svg)
### ResponsePattern Between
```
Between "Q" and "R", it is always the case that if "T" holds, then "S" eventually holds
```
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && (!S && T))⌉;⌈(!R && !S)⌉;⌈R⌉;true
```
![](../../img/patterns/ResponsePattern_Between.svg)
