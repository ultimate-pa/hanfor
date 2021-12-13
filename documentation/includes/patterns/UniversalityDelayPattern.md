<!-- Auto generated file, do not make any changes here. -->

## UniversalityDelayPattern

### UniversalityDelayPattern Globally
```
Globally, it is always the case that "R" holds after at most "5" time units
```

#### Countertraces
```
⌈true⌉ ∧ ℓ ≥ 5;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityDelayPattern_Globally_0.svg)

#### Examples



### UniversalityDelayPattern Before
```
Before "P", it is always the case that "R" holds after at most "5" time units
```

#### Countertraces
```
⌈!P⌉ ∧ ℓ ≥ 5;⌈(!P && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityDelayPattern_Before_0.svg)

#### Examples



### UniversalityDelayPattern After
```
After "P", it is always the case that "R" holds after at most "5" time units
```

#### Countertraces
```
true;⌈P⌉;⌈true⌉ ∧ ℓ ≥ 5;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityDelayPattern_After_0.svg)

#### Examples



### UniversalityDelayPattern Between
```
Between "P" and "Q", it is always the case that "R" holds after at most "5" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉ ∧ ℓ ≥ 5;⌈(!Q && !R)⌉;true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityDelayPattern_Between_0.svg)

#### Examples



### UniversalityDelayPattern AfterUntil
```
After "P" until "Q", it is always the case that "R" holds after at most "5" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉ ∧ ℓ ≥ 5;⌈(!Q && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityDelayPattern_AfterUntil_0.svg)

#### Examples


