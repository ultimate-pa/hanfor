<!-- Auto generated file, do not make any changes here. -->

## PrecedenceChain12Pattern

### PrecedenceChain12Pattern Globally
```
Globally, it is always the case that if "R" holds and is succeeded by "S", then "T" previously held
```

#### Countertraces
```
⌈!T⌉;⌈R⌉;true;⌈S⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedenceChain12Pattern_Globally_0.svg)

#### Examples



### PrecedenceChain12Pattern Before
```
Before "P", it is always the case that if "R" holds and is succeeded by "S", then "T" previously held
```

#### Countertraces
```
⌈(!P && !T)⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedenceChain12Pattern_Before_0.svg)

#### Examples



### PrecedenceChain12Pattern After
```
After "P", it is always the case that if "R" holds and is succeeded by "S", then "T" previously held
```

#### Countertraces
```
true;⌈P⌉;⌈!T⌉;⌈R⌉;true;⌈S⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedenceChain12Pattern_After_0.svg)

#### Examples



### PrecedenceChain12Pattern Between
```
Between "P" and "Q", it is always the case that if "R" holds and is succeeded by "S", then "T" previously held
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedenceChain12Pattern_Between_0.svg)

#### Examples



### PrecedenceChain12Pattern AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds and is succeeded by "S", then "T" previously held
```

#### Countertraces
```
true;⌈P⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedenceChain12Pattern_AfterUntil_0.svg)

#### Examples


