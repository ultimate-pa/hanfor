<!-- Auto generated file, do not make any changes here. -->

## BndEntryConditionPattern

### BndEntryConditionPattern Globally
```
Globally, it is always the case that after "R" holds for "5" time units, then "Q" holds
```
```
true;⌈R⌉ ∧ ℓ > 5;⌈!Q⌉;true
```
![](../../img/patterns/BndEntryConditionPattern_Globally.svg)
### BndEntryConditionPattern Before
```
Before "Q", it is always the case that after "S" holds for "5" time units, then "R" holds
```
```
⌈!Q⌉;⌈(!Q && S)⌉ ∧ ℓ > 5;⌈(!Q && !R)⌉;true
```
![](../../img/patterns/BndEntryConditionPattern_Before.svg)
### BndEntryConditionPattern After
```
After "Q", it is always the case that after "S" holds for "5" time units, then "R" holds
```
```
true;⌈Q⌉;true;⌈S⌉ ∧ ℓ > 5;⌈!R⌉;true
```
![](../../img/patterns/BndEntryConditionPattern_After.svg)
### BndEntryConditionPattern Between
```
Between "Q" and "R", it is always the case that after "T" holds for "5" time units, then "S" holds
```
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && T)⌉ ∧ ℓ > 5;⌈(!R && !S)⌉;⌈!R⌉;⌈R⌉;true
```
![](../../img/patterns/BndEntryConditionPattern_Between.svg)
### BndEntryConditionPattern AfterUntil
```
After "Q" until "R", it is always the case that after "T" holds for "5" time units, then "S" holds
```
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && T)⌉ ∧ ℓ > 5;⌈(!R && !S)⌉;true
```
![](../../img/patterns/BndEntryConditionPattern_AfterUntil.svg)
