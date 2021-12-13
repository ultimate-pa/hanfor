<!-- Auto generated file, do not make any changes here. -->

## InvariancePattern

### InvariancePattern Globally
```
Globally, it is always the case that if "R" holds, then "S" holds as well
```

#### Countertraces
```
true;⌈(R && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvariancePattern_Globally_0.svg)

#### Examples



### InvariancePattern Before
```
Before "P", it is always the case that if "R" holds, then "S" holds as well
```

#### Countertraces
```
⌈!P⌉;⌈(!P && (R && !S))⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvariancePattern_Before_0.svg)

#### Examples



### InvariancePattern After
```
After "P", it is always the case that if "R" holds, then "S" holds as well
```

#### Countertraces
```
true;⌈P⌉;true;⌈(R && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvariancePattern_After_0.svg)

#### Examples



### InvariancePattern Between
```
Between "P" and "Q", it is always the case that if "R" holds, then "S" holds as well
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvariancePattern_Between_0.svg)

#### Examples



### InvariancePattern AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then "S" holds as well
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvariancePattern_AfterUntil_0.svg)

#### Examples


