toc_depth: 2

<!-- Auto generated file, do not make changes here. -->

## ResponseChain21Pattern Before
```
Before "Q", it is always the case that if "U" holds and is succeeded by "T", then "S" eventually holds after "R"
```
```
⌈!Q⌉;⌈(!Q && (!R && S))⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !T)⌉;⌈Q⌉;true
```
![](/img/patterns/ResponseChain21Pattern_Before.svg)
## ResponseChain21Pattern Between
```
Between "Q" and "R", it is always the case that if "V" holds and is succeeded by "U", then "T" eventually holds after "S"
```
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && (!S && T))⌉;⌈!R⌉;⌈(!R && S)⌉;⌈(!R && !U)⌉;⌈R⌉;true
```
![](/img/patterns/ResponseChain21Pattern_Between.svg)
