<!-- Auto generated file, do not make any changes here. -->

## TriggerResponseBoundL1Pattern

### TriggerResponseBoundL1Pattern Globally
```
Globally, it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds
```

#### Countertraces
```
true;⌈R⌉ ∧ ℓ ≥ 5;⌈(R && (S && !T))⌉;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseBoundL1Pattern_Globally_0.svg)

#### Examples



### TriggerResponseBoundL1Pattern Before
```
Before "P", it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ 5;⌈(!P && (R && (S && !T)))⌉;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseBoundL1Pattern_Before_0.svg)

#### Examples



### TriggerResponseBoundL1Pattern After
```
After "P", it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ 5;⌈(R && (S && !T))⌉;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseBoundL1Pattern_After_0.svg)

#### Examples



### TriggerResponseBoundL1Pattern Between
```
Between "P" and "Q", it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && (R && (S && !T)))⌉;true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseBoundL1Pattern_Between_0.svg)

#### Examples



### TriggerResponseBoundL1Pattern AfterUntil
```
After "P" until "Q", it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && (R && (S && !T)))⌉;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseBoundL1Pattern_AfterUntil_0.svg)

#### Examples


