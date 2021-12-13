<!-- Auto generated file, do not make any changes here. -->

## ResponseBoundL12Pattern

### ResponseBoundL12Pattern Globally
```
Globally, it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards for at least "10" time units
```

#### Countertraces
```
true;⌈R⌉ ∧ ℓ ≥ 5;⌈S⌉ ∧ ℓ <₀ 10;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL12Pattern_Globally_0.svg)

#### Examples



### ResponseBoundL12Pattern Before
```
Before "P", it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards for at least "10" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ 5;⌈(!P && S)⌉ ∧ ℓ <₀ 10;⌈(!P && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL12Pattern_Before_0.svg)

#### Examples



### ResponseBoundL12Pattern After
```
After "P", it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards for at least "10" time units
```

#### Countertraces
```
true;⌈P⌉;⌈R⌉ ∧ ℓ ≥ 5;⌈S⌉ ∧ ℓ <₀ 10;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL12Pattern_After_0.svg)

#### Examples



### ResponseBoundL12Pattern Between
```
Between "P" and "Q", it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards for at least "10" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && S)⌉ ∧ ℓ <₀ 10;⌈(!Q && !S)⌉;true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL12Pattern_Between_0.svg)

#### Examples



### ResponseBoundL12Pattern AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards for at least "10" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && S)⌉ ∧ ℓ <₀ 10;⌈(!Q && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL12Pattern_AfterUntil_0.svg)

#### Examples


