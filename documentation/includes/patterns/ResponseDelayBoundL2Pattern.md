<!-- Auto generated file, do not make any changes here. -->

## ResponseDelayBoundL2Pattern

### ResponseDelayBoundL2Pattern Globally
```
Globally, it is always the case that if "R" holds, then "S" holds after at most "5" time units for at least "10" time units
```

#### Countertraces
```
true;⌈R⌉;⌈!S⌉ ∧ ℓ > 5;true
true;⌈R⌉;⌈!S⌉ ∧ ℓ <₀ 5;⌈S⌉ ∧ ℓ < 10;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayBoundL2Pattern_Globally_0.svg)
![](../img/patterns/ResponseDelayBoundL2Pattern_Globally_1.svg)

#### Examples



### ResponseDelayBoundL2Pattern Before
```
Before "P", it is always the case that if "R" holds, then "S" holds after at most "5" time units for at least "10" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉ ∧ ℓ > 5;true
⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉ ∧ ℓ <₀ 5;⌈(!P && S)⌉ ∧ ℓ < 10;⌈(!P && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayBoundL2Pattern_Before_0.svg)
![](../img/patterns/ResponseDelayBoundL2Pattern_Before_1.svg)

#### Examples



### ResponseDelayBoundL2Pattern After
```
After "P", it is always the case that if "R" holds, then "S" holds after at most "5" time units for at least "10" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉;⌈!S⌉ ∧ ℓ > 5;true
true;⌈P⌉;true;⌈R⌉;⌈!S⌉ ∧ ℓ <₀ 5;⌈S⌉ ∧ ℓ < 10;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayBoundL2Pattern_After_0.svg)
![](../img/patterns/ResponseDelayBoundL2Pattern_After_1.svg)

#### Examples



### ResponseDelayBoundL2Pattern Between
```
Between "P" and "Q", it is always the case that if "R" holds, then "S" holds after at most "5" time units for at least "10" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ > 5;true;⌈Q⌉;true
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ <₀ 5;⌈(!Q && S)⌉ ∧ ℓ < 10;⌈(!Q && !S)⌉;true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayBoundL2Pattern_Between_0.svg)
![](../img/patterns/ResponseDelayBoundL2Pattern_Between_1.svg)

#### Examples



### ResponseDelayBoundL2Pattern AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then "S" holds after at most "5" time units for at least "10" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ > 5;true
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ <₀ 5;⌈(!Q && S)⌉ ∧ ℓ < 10;⌈(!Q && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayBoundL2Pattern_AfterUntil_0.svg)
![](../img/patterns/ResponseDelayBoundL2Pattern_AfterUntil_1.svg)

#### Examples


