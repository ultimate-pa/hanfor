<!-- Auto generated file, do not make any changes here. -->

## InitializationPattern

### InitializationPattern Globally
```
Globally, it is always the case that initially "R" holds
```

#### Countertraces
```
⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/InitializationPattern_Globally_0.svg)

#### Examples



### InitializationPattern Before
```
Before "P", it is always the case that initially "R" holds
```

#### Countertraces
```
⌈(!P && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/InitializationPattern_Before_0.svg)

#### Examples



### InitializationPattern After
```
After "P", it is always the case that initially "R" holds
```

#### Countertraces
```
true;⌈P⌉;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/InitializationPattern_After_0.svg)

#### Examples



### InitializationPattern Between
```
Between "P" and "Q", it is always the case that initially "R" holds
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈(!Q && !R)⌉;true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/InitializationPattern_Between_0.svg)

#### Examples



### InitializationPattern AfterUntil
```
After "P" until "Q", it is always the case that initially "R" holds
```

#### Countertraces
```
true;⌈P⌉;⌈(!Q && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/InitializationPattern_AfterUntil_0.svg)

#### Examples


