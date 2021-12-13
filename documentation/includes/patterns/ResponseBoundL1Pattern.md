<!-- Auto generated file, do not make any changes here. -->

## ResponseBoundL1Pattern

### ResponseBoundL1Pattern Globally
```
Globally, it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards
```

#### Countertraces
```
true;⌈R⌉ ∧ ℓ ≥ 5;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL1Pattern_Globally_0.svg)

#### Examples



### ResponseBoundL1Pattern Before
```
Before "P", it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ 5;⌈(!P && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL1Pattern_Before_0.svg)

#### Examples



### ResponseBoundL1Pattern After
```
After "P", it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ 5;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL1Pattern_After_0.svg)

#### Examples



### ResponseBoundL1Pattern Between
```
Between "P" and "Q", it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && !S)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL1Pattern_Between_0.svg)

#### Examples



### ResponseBoundL1Pattern AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL1Pattern_AfterUntil_0.svg)

#### Examples


