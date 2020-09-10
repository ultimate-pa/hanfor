<!-- Auto generated file, do not make any changes here. -->

## PrecedenceChain21Pattern

### PrecedenceChain21Pattern Globally
```
Globally, it is always the case that if "S" holds, then "R" previously held and was preceded by "Q"
```

```
Countertraces: (⌈!Q⌉;⌈S⌉;true), (⌈!R⌉;⌈S⌉;true), (⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(Q && !R)⌉;⌈!R⌉;⌈S⌉;true)
```

![](../img/patterns/PrecedenceChain21Pattern_Globally_0.svg)

![](../img/patterns/PrecedenceChain21Pattern_Globally_1.svg)

![](../img/patterns/PrecedenceChain21Pattern_Globally_2.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/PrecedenceChain21Pattern_Globally_0.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain21Pattern_Globally_1.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain21Pattern_Globally_2.svg) |  |


### PrecedenceChain21Pattern Before
```
Before "Q", it is always the case that if "T" holds, then "S" previously held and was preceded by "R"
```

```
Countertraces: (⌈(!Q && !R)⌉;⌈(!Q && T)⌉;true), (⌈(!Q && !S)⌉;⌈(!Q && T)⌉;true), (⌈(!Q && !R)⌉;⌈(!Q && (!R && S))⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉;⌈(!Q && T)⌉;true)
```

![](../img/patterns/PrecedenceChain21Pattern_Before_0.svg)

![](../img/patterns/PrecedenceChain21Pattern_Before_1.svg)

![](../img/patterns/PrecedenceChain21Pattern_Before_2.svg)

<div class="pattern-examples"></div>
| Positive Example | Negative Example |
| --- | --- |
| ![](../img/failure_paths/positive/PrecedenceChain21Pattern_Before_0.svg) |  |
| ![](../img/failure_paths/positive/PrecedenceChain21Pattern_Before_1.svg) |  |


### PrecedenceChain21Pattern After
```
After "Q", it is always the case that if "T" holds, then "S" previously held and was preceded by "R"
```

```
Countertraces: (true;⌈Q⌉;⌈!R⌉;⌈T⌉;true), (true;⌈Q⌉;⌈!S⌉;⌈T⌉;true), (true;⌈Q⌉;⌈!R⌉;⌈(!R && S)⌉;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉;⌈T⌉;true)
```

![](../img/patterns/PrecedenceChain21Pattern_After_0.svg)

![](../img/patterns/PrecedenceChain21Pattern_After_1.svg)

![](../img/patterns/PrecedenceChain21Pattern_After_2.svg)


### PrecedenceChain21Pattern Between
```
Between "Q" and "R", it is always the case that if "U" holds, then "T" previously held and was preceded by "S"
```

```
Countertraces: (true;⌈(Q && !R)⌉;⌈(!R && !S)⌉;⌈(!R && U)⌉;⌈!R⌉;⌈R⌉;true), (true;⌈(Q && !R)⌉;⌈(!R && !T)⌉;⌈(!R && U)⌉;⌈!R⌉;⌈R⌉;true), (true;⌈(Q && !R)⌉;⌈(!R && !S)⌉;⌈(!R && (!S && T))⌉;⌈(!R && !S)⌉;⌈(!R && (S && !T))⌉;⌈(!R && !T)⌉;⌈(!R && U)⌉;⌈!R⌉;⌈R⌉;true)
```

![](../img/patterns/PrecedenceChain21Pattern_Between_0.svg)

![](../img/patterns/PrecedenceChain21Pattern_Between_1.svg)

![](../img/patterns/PrecedenceChain21Pattern_Between_2.svg)


### PrecedenceChain21Pattern AfterUntil
```
After "Q" until "R", it is always the case that if "U" holds, then "T" previously held and was preceded by "S"
```

```
Countertraces: (true;⌈Q⌉;⌈(!R && !S)⌉;⌈(!R && U)⌉;true), (true;⌈Q⌉;⌈(!R && !T)⌉;⌈(!R && U)⌉;true), (true;⌈Q⌉;⌈(!R && !S)⌉;⌈(!R && (!S && T))⌉;⌈(!R && !S)⌉;⌈(!R && (S && !T))⌉;⌈(!R && !T)⌉;⌈(!R && U)⌉;true)
```

![](../img/patterns/PrecedenceChain21Pattern_AfterUntil_0.svg)

![](../img/patterns/PrecedenceChain21Pattern_AfterUntil_1.svg)

![](../img/patterns/PrecedenceChain21Pattern_AfterUntil_2.svg)

