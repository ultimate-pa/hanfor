<!-- Auto generated file, do not make any changes here. -->

## ConstrainedChainPattern

### ConstrainedChainPattern Before
```
Before "P", it is always the case that if "R" holds, then "S" eventually holds and is succeeded by "T" where "U" does not hold between "S" and "T"
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉;⌈P⌉;true
⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;⌈(!P && !T)⌉;⌈P⌉;true
⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;⌈(!P && !T)⌉;⌈(!P && (!T && U))⌉;⌈!P⌉;⌈(!P && T)⌉;⌈!P⌉;⌈P⌉;true
```

#### Phase Event Automata
![](../img/patterns/ConstrainedChainPattern_Before_0.svg)
![](../img/patterns/ConstrainedChainPattern_Before_1.svg)
![](../img/patterns/ConstrainedChainPattern_Before_2.svg)

#### Examples



### ConstrainedChainPattern Between
```
Between "P" and "Q", it is always the case that if "R" holds, then "S" eventually holds and is succeeded by "T" where "U" does not hold between "S" and "T"
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉;⌈Q⌉;true
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈Q⌉;true
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈(!Q && (!T && U))⌉;⌈!Q⌉;⌈(!Q && T)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ConstrainedChainPattern_Between_0.svg)
![](../img/patterns/ConstrainedChainPattern_Between_1.svg)
![](../img/patterns/ConstrainedChainPattern_Between_2.svg)

#### Examples



### ConstrainedChainPattern AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then "S" eventually holds and is succeeded by "T" where "U" does not hold between "S" and "T"
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉;⌈Q⌉;true
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈Q⌉;true
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈(!Q && (!T && U))⌉;⌈!Q⌉;⌈(!Q && T)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ConstrainedChainPattern_AfterUntil_0.svg)
![](../img/patterns/ConstrainedChainPattern_AfterUntil_1.svg)
![](../img/patterns/ConstrainedChainPattern_AfterUntil_2.svg)

#### Examples


