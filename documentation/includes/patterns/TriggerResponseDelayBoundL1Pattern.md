<!-- Auto generated file, do not make any changes here. -->

## TriggerResponseDelayBoundL1Pattern

### TriggerResponseDelayBoundL1Pattern Globally
```
Globally, it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds after at most "10" time units
```

#### Countertraces
```
true;⌈R⌉ ∧ ℓ ≥ 5;⌈(R && (S && !T))⌉;⌈!T⌉ ∧ ℓ > 10;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseDelayBoundL1Pattern_Globally_0.svg)

#### Examples



### TriggerResponseDelayBoundL1Pattern Before
```
Before "P", it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds after at most "10" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ 5;⌈(!P && (R && (S && !T)))⌉;⌈(!P && !T)⌉ ∧ ℓ > 10;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseDelayBoundL1Pattern_Before_0.svg)

#### Examples



### TriggerResponseDelayBoundL1Pattern After
```
After "P", it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds after at most "10" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ 5;⌈(R && (S && !T))⌉;⌈!T⌉ ∧ ℓ > 10;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseDelayBoundL1Pattern_After_0.svg)

#### Examples



### TriggerResponseDelayBoundL1Pattern Between
```
Between "P" and "Q", it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds after at most "10" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && (R && (S && !T)))⌉;⌈(!Q && !T)⌉ ∧ ℓ > 10;true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseDelayBoundL1Pattern_Between_0.svg)

#### Examples



### TriggerResponseDelayBoundL1Pattern AfterUntil
```
After "P" until "Q", it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds after at most "10" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && (R && (S && !T)))⌉;⌈(!Q && !T)⌉ ∧ ℓ > 10;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseDelayBoundL1Pattern_AfterUntil_0.svg)

#### Examples


