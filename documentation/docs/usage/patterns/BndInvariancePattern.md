<!-- Auto generated file, do not make any changes here. -->

## BndInvariancePattern

### BndInvariancePattern Globally
```
Globally, it is always the case that if "R" holds, then "Q" holds for at least "c0" time units
```
```
true;⌈R⌉;⌈true⌉ ∧ ℓ < 50;⌈!Q⌉;true
```
![](/img/patterns/BndInvariancePattern_Globally.svg)
### BndInvariancePattern Before
```
Before "Q", it is always the case that if "S" holds, then "R" holds for at least "c0" time units
```
```
⌈!Q⌉;⌈(!Q && S)⌉;⌈!Q⌉ ∧ ℓ < 50;⌈(!Q && !R)⌉;true
```
![](/img/patterns/BndInvariancePattern_Before.svg)
### BndInvariancePattern After
```
After "Q", it is always the case that if "S" holds, then "R" holds for at least "c0" time units
```
```
true;⌈Q⌉;true;⌈S⌉;⌈true⌉ ∧ ℓ < 50;⌈!R⌉;true
```
![](/img/patterns/BndInvariancePattern_After.svg)
### BndInvariancePattern Between
```
Between "Q" and "R", it is always the case that if "T" holds, then "S" holds for at least "c0" time units
```
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && T)⌉;⌈!R⌉ ∧ ℓ < 50;⌈(!R && !S)⌉;⌈!R⌉;⌈R⌉;true
```
![](/img/patterns/BndInvariancePattern_Between.svg)
### BndInvariancePattern AfterUntil
```
After "Q" until "R", it is always the case that if "T" holds, then "S" holds for at least "c0" time units
```
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && T)⌉;⌈!R⌉ ∧ ℓ < 50;⌈(!R && !S)⌉;true
```
![](/img/patterns/BndInvariancePattern_AfterUntil.svg)
