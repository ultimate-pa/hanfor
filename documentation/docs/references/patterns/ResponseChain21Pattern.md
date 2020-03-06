<!-- Auto generated file, do not make any changes here. -->

## ResponseChain21Pattern

### ResponseChain21Pattern Before
```
Before "Q", it is always the case that if "U" holds and is succeeded by "T", then "S" eventually holds after "R"
```
```
Counterexample: ⌈!Q⌉;⌈(!Q && U)⌉;⌈!Q⌉;⌈(!Q && T)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉;⌈!Q⌉;⌈Q⌉;true
```

![](../img/patterns/ResponseChain21Pattern_Before.svg)

![](../img/failure_paths/ResponseChain21Pattern_Before_0.svg)


### ResponseChain21Pattern Between
```
Between "Q" and "R", it is always the case that if "V" holds and is succeeded by "U", then "T" eventually holds after "S"
```
```
Counterexample: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && V)⌉;⌈!R⌉;⌈(!R && U)⌉;⌈!R⌉;⌈(!R && S)⌉;⌈(!R && !T)⌉;⌈R⌉;true
```

![](../img/patterns/ResponseChain21Pattern_Between.svg)

