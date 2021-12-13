<!-- Auto generated file, do not make any changes here. -->

## ResponseChain12Pattern

### ResponseChain12Pattern Before
```
Before "P", it is always the case that if "R" holds, then "S" eventually holds and is succeeded by "T"
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉;⌈P⌉;true
⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;⌈(!P && !T)⌉;⌈P⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseChain12Pattern_Before_0.svg)
![](../img/patterns/ResponseChain12Pattern_Before_1.svg)

#### Examples



### ResponseChain12Pattern Between
```
Between "P" and "Q", it is always the case that if "R" holds, then "S" eventually holds and is succeeded by "T"
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉;⌈Q⌉;true
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseChain12Pattern_Between_0.svg)
![](../img/patterns/ResponseChain12Pattern_Between_1.svg)

#### Examples



### ResponseChain12Pattern AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then "S" eventually holds and is succeeded by "T"
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉;⌈Q⌉;true
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseChain12Pattern_AfterUntil_0.svg)
![](../img/patterns/ResponseChain12Pattern_AfterUntil_1.svg)

#### Examples


