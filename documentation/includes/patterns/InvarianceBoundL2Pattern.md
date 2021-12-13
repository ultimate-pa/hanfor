<!-- Auto generated file, do not make any changes here. -->

## InvarianceBoundL2Pattern

### InvarianceBoundL2Pattern Globally
```
Globally, it is always the case that if "R" holds, then "S" holds for at least "5" time units
```

#### Countertraces
```
true;⌈R⌉;⌈true⌉ ∧ ℓ < 5;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvarianceBoundL2Pattern_Globally_0.svg)

#### Examples



### InvarianceBoundL2Pattern Before
```
Before "P", it is always the case that if "R" holds, then "S" holds for at least "5" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉ ∧ ℓ < 5;⌈(!P && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvarianceBoundL2Pattern_Before_0.svg)

#### Examples



### InvarianceBoundL2Pattern After
```
After "P", it is always the case that if "R" holds, then "S" holds for at least "5" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉;⌈true⌉ ∧ ℓ < 5;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvarianceBoundL2Pattern_After_0.svg)

#### Examples



### InvarianceBoundL2Pattern Between
```
Between "P" and "Q", it is always the case that if "R" holds, then "S" holds for at least "5" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < 5;⌈(!Q && !S)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvarianceBoundL2Pattern_Between_0.svg)

#### Examples



### InvarianceBoundL2Pattern AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then "S" holds for at least "5" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < 5;⌈(!Q && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvarianceBoundL2Pattern_AfterUntil_0.svg)

#### Examples


