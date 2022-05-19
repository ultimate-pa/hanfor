<!-- Auto generated file, do not make any changes here. -->

## Persistence

### Persistence Globally
```
Globally, it is always the case that if "R" holds, then it holds persistently
```

#### Countertraces
```
true;⌈R⌉;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/PersistencePattern_Globally_0.svg)



### Persistence Before
```
Before "P", it is always the case that if "R" holds, then it holds persistently
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/PersistencePattern_Before_0.svg)



### Persistence After
```
After "P", it is always the case that if "R" holds, then it holds persistently
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/PersistencePattern_After_0.svg)



### Persistence Between
```
Between "P" and "Q", it is always the case that if "R" holds, then it holds persistently
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/PersistencePattern_Between_0.svg)



### Persistence AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then it holds persistently
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/PersistencePattern_AfterUntil_0.svg)


