<!-- Auto generated file, do not make any changes here. -->

## BndRecurrencePattern

### BndRecurrencePattern Globally
```
Globally, it is always the case that "Q" holds at least every "5" time units
```
```
Counterexample: true;⌈!Q⌉ ∧ ℓ > 5;true
```
![](../img/patterns/BndRecurrencePattern_Globally.svg)
### BndRecurrencePattern Before
```
Before "Q", it is always the case that "R" holds at least every "5" time units
```
```
Counterexample: ⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > 5;true
```
![](../img/patterns/BndRecurrencePattern_Before.svg)
### BndRecurrencePattern After
```
After "Q", it is always the case that "R" holds at least every "5" time units
```
```
Counterexample: true;⌈Q⌉;true;⌈!R⌉ ∧ ℓ > 5;true
```
![](../img/patterns/BndRecurrencePattern_After.svg)
### BndRecurrencePattern Between
```
Between "Q" and "R", it is always the case that "S" holds at least every "5" time units
```
```
Counterexample: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !S)⌉ ∧ ℓ > 5;⌈!R⌉;⌈R⌉;true
```
![](../img/patterns/BndRecurrencePattern_Between.svg)
### BndRecurrencePattern AfterUntil
```
After "Q" until "R", it is always the case that "S" holds at least every "5" time units
```
```
Counterexample: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !S)⌉ ∧ ℓ > 5;true
```
![](../img/patterns/BndRecurrencePattern_AfterUntil.svg)
