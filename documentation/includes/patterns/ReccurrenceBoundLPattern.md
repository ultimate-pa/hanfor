<!-- Auto generated file, do not make any changes here. -->

## ReccurrenceBoundLPattern

### ReccurrenceBoundLPattern Globally
```
Globally, it is always the case that "R" holds at least every "5" time units
```

#### Countertraces
```
true;⌈!R⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/ReccurrenceBoundLPattern_Globally_0.svg)

#### Examples



### ReccurrenceBoundLPattern Before
```
Before "P", it is always the case that "R" holds at least every "5" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && !R)⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/ReccurrenceBoundLPattern_Before_0.svg)

#### Examples



### ReccurrenceBoundLPattern After
```
After "P", it is always the case that "R" holds at least every "5" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈!R⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/ReccurrenceBoundLPattern_After_0.svg)

#### Examples



### ReccurrenceBoundLPattern Between
```
Between "P" and "Q", it is always the case that "R" holds at least every "5" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > 5;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ReccurrenceBoundLPattern_Between_0.svg)

#### Examples



### ReccurrenceBoundLPattern AfterUntil
```
After "P" until "Q", it is always the case that "R" holds at least every "5" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/ReccurrenceBoundLPattern_AfterUntil_0.svg)

#### Examples


