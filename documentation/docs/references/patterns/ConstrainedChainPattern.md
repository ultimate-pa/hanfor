<!-- Auto generated file, do not make any changes here. -->

## ConstrainedChainPattern

### ConstrainedChainPattern Before
```
Before "Q", it is always the case that if "W" holds, then "V" eventually holds and is succeeded by "U" where "T" does not hold between "V" and "U"
```

#### Countertraces
```
⌈!Q⌉;⌈(!Q && W)⌉;⌈(!Q && !V)⌉;⌈Q⌉;true
⌈!Q⌉;⌈(!Q && W)⌉;⌈!Q⌉;⌈(!Q && V)⌉;⌈(!Q && !U)⌉;⌈Q⌉;true
⌈!Q⌉;⌈(!Q && W)⌉;⌈!Q⌉;⌈(!Q && V)⌉;⌈(!Q && !U)⌉;⌈(!Q && (T && !U))⌉;⌈!Q⌉;⌈(!Q && U)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ConstrainedChainPattern_Before_0.svg)
![](../img/patterns/ConstrainedChainPattern_Before_1.svg)
![](../img/patterns/ConstrainedChainPattern_Before_2.svg)

#### Examples



### ConstrainedChainPattern Between
```
Between "Q" and "R", it is always the case that if "X" holds, then "W" eventually holds and is succeeded by "V" where "U" does not hold between "W" and "V"
```

#### Countertraces
```
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && X)⌉;⌈(!R && !W)⌉;⌈R⌉;true
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && X)⌉;⌈!R⌉;⌈(!R && W)⌉;⌈(!R && !V)⌉;⌈R⌉;true
true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && X)⌉;⌈!R⌉;⌈(!R && W)⌉;⌈(!R && !V)⌉;⌈(!R && (U && !V))⌉;⌈!R⌉;⌈(!R && V)⌉;⌈!R⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/ConstrainedChainPattern_Between_0.svg)
![](../img/patterns/ConstrainedChainPattern_Between_1.svg)
![](../img/patterns/ConstrainedChainPattern_Between_2.svg)

#### Examples



### ConstrainedChainPattern AfterUntil
```
After "Q" until "R", it is always the case that if "X" holds, then "W" eventually holds and is succeeded by "V" where "U" does not hold between "W" and "V"
```

#### Countertraces
```
true;⌈Q⌉;⌈!R⌉;⌈(!R && X)⌉;⌈(!R && !W)⌉;⌈R⌉;true
true;⌈Q⌉;⌈!R⌉;⌈(!R && X)⌉;⌈!R⌉;⌈(!R && W)⌉;⌈(!R && !V)⌉;⌈R⌉;true
true;⌈Q⌉;⌈!R⌉;⌈(!R && X)⌉;⌈!R⌉;⌈(!R && W)⌉;⌈(!R && !V)⌉;⌈(!R && (U && !V))⌉;⌈!R⌉;⌈(!R && V)⌉;⌈!R⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/ConstrainedChainPattern_AfterUntil_0.svg)
![](../img/patterns/ConstrainedChainPattern_AfterUntil_1.svg)
![](../img/patterns/ConstrainedChainPattern_AfterUntil_2.svg)

#### Examples


