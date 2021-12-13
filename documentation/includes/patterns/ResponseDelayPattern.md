<!-- Auto generated file, do not make any changes here. -->

## ResponseDelayPattern

### ResponseDelayPattern Globally
```
Globally, it is always the case that if "R" holds, then "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayPattern_Globally_0.svg)

#### Examples



### ResponseDelayPattern Before
```
Before "P", it is always the case that if "R" holds, then "S" holds after at most "5" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayPattern_Before_0.svg)

#### Examples



### ResponseDelayPattern After
```
After "P", it is always the case that if "R" holds, then "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayPattern_After_0.svg)

#### Examples



### ResponseDelayPattern Between
```
Between "P" and "Q", it is always the case that if "R" holds, then "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > 5;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayPattern_Between_0.svg)

#### Examples



### ResponseDelayPattern AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayPattern_AfterUntil_0.svg)

#### Examples


