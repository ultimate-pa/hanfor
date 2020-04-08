<!-- Auto generated file, do not make any changes here. -->

## PrecedenceChain12Pattern

### PrecedenceChain12Pattern Globally
```
Globally, it is always the case that if "S" holds and is succeeded by "R", then "Q" previously held
```

```
Countertraces: (⌈!Q⌉;⌈S⌉;true;⌈R⌉;true)
```

![](../img/patterns/PrecedenceChain12Pattern_Globally_0.svg)


### PrecedenceChain12Pattern Before
```
Before "Q", it is always the case that if "T" holds and is succeeded by "S", then "R" previously held
```

```
Countertraces: (⌈(!Q && !R)⌉;⌈(!Q && T)⌉;⌈!Q⌉;⌈(!Q && S)⌉;true)
```

![](../img/patterns/PrecedenceChain12Pattern_Before_0.svg)


### PrecedenceChain12Pattern After
```
After "Q", it is always the case that if "T" holds and is succeeded by "S", then "R" previously held
```

```
Countertraces: (⌈!T⌉;⌈(Q && !T)⌉;⌈!T⌉;⌈(S && !T)⌉;true;⌈R⌉;true)
```

![](../img/patterns/PrecedenceChain12Pattern_After_0.svg)


### PrecedenceChain12Pattern Between
```
Between "Q" and "R", it is always the case that if "U" holds and is succeeded by "T", then "S" previously held
```

```
Countertraces: (⌈!U⌉;⌈(Q && (!R && !U))⌉;⌈(!R && !U)⌉;⌈(!R && (T && !U))⌉;⌈!R⌉;⌈(!R && S)⌉;⌈!R⌉;⌈R⌉;true)
```

![](../img/patterns/PrecedenceChain12Pattern_Between_0.svg)


### PrecedenceChain12Pattern AfterUntil
```
After "Q" until "R", it is always the case that if "U" holds and is succeeded by "T", then "S" previously held
```

```
Countertraces: (⌈!U⌉;⌈(Q && (!R && !U))⌉;⌈(!R && !U)⌉;⌈(!R && (T && !U))⌉;⌈!R⌉;⌈(!R && S)⌉;true)
```

![](../img/patterns/PrecedenceChain12Pattern_AfterUntil_0.svg)

