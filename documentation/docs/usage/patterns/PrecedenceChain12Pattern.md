toc_depth: 2

<!-- Auto generated file, do not make changes here. -->

## PrecedenceChain12Pattern Globally
```
Globally, it is always the case that if "S" holds and is succeeded by "R", then "Q" previously held
```
```
⌈!S⌉;⌈R⌉;true;⌈Q⌉;true
```
![](/img/patterns/PrecedenceChain12Pattern_Globally.svg)
## PrecedenceChain12Pattern Before
```
Before "Q", it is always the case that if "T" holds and is succeeded by "S", then "R" previously held
```
```
⌈(!Q && !T)⌉;⌈(!Q && (S && !T))⌉;⌈!Q⌉;⌈(!Q && R)⌉;true
```
![](/img/patterns/PrecedenceChain12Pattern_Before.svg)
## PrecedenceChain12Pattern After
```
After "Q", it is always the case that if "T" holds and is succeeded by "S", then "R" previously held
```
```
⌈!T⌉;⌈(Q && !T)⌉;⌈!T⌉;⌈(S && !T)⌉;true;⌈R⌉;true
```
![](/img/patterns/PrecedenceChain12Pattern_After.svg)
## PrecedenceChain12Pattern Between
```
Between "Q" and "R", it is always the case that if "U" holds and is succeeded by "T", then "S" previously held
```
```
⌈!U⌉;⌈(Q && (!R && !U))⌉;⌈(!R && !U)⌉;⌈(!R && (T && !U))⌉;⌈!R⌉;⌈(!R && S)⌉;⌈!R⌉;⌈R⌉;true
```
![](/img/patterns/PrecedenceChain12Pattern_Between.svg)
## PrecedenceChain12Pattern AfterUntil
```
After "Q" until "R", it is always the case that if "U" holds and is succeeded by "T", then "S" previously held
```
```
⌈!U⌉;⌈(Q && (!R && !U))⌉;⌈(!R && !U)⌉;⌈(!R && (T && !U))⌉;⌈!R⌉;⌈(!R && S)⌉;true
```
![](/img/patterns/PrecedenceChain12Pattern_AfterUntil.svg)
