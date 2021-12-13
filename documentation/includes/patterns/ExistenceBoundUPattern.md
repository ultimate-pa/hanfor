<!-- Auto generated file, do not make any changes here. -->

## ExistenceBoundUPattern

### ExistenceBoundUPattern Globally
```
Globally, transitions to states in which "R" holds occur at most twice
```

#### Countertraces
```
true;⌈R⌉;⌈!R⌉;⌈R⌉;⌈!R⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/ExistenceBoundUPattern_Globally_0.svg)

#### Examples



### ExistenceBoundUPattern Before
```
Before "P", transitions to states in which "R" holds occur at most twice
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/ExistenceBoundUPattern_Before_0.svg)

#### Examples



### ExistenceBoundUPattern After
```
After "P", transitions to states in which "R" holds occur at most twice
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉;⌈!R⌉;⌈R⌉;⌈!R⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/ExistenceBoundUPattern_After_0.svg)

#### Examples



### ExistenceBoundUPattern Between
```
Between "P" and "Q", transitions to states in which "R" holds occur at most twice
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ExistenceBoundUPattern_Between_0.svg)

#### Examples



### ExistenceBoundUPattern AfterUntil
```
After "P" until "Q", transitions to states in which "R" holds occur at most twice
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/ExistenceBoundUPattern_AfterUntil_0.svg)

#### Examples


