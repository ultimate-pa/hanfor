<!-- Auto generated file, do not make any changes here. -->

## DurationBoundL

### DurationBoundL Globally
```
Globally, it is always the case that once "R" becomes satisfied, it holds for at least "5" time units
```

#### Countertraces
```
true;⌈!R⌉;⌈R⌉ ∧ ℓ < 5;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/DurationBoundLPattern_Globally_0.svg)



### DurationBoundL Before
```
Before "P", it is always the case that once "R" becomes satisfied, it holds for at least "5" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉ ∧ ℓ < 5;⌈(!P && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/DurationBoundLPattern_Before_0.svg)



### DurationBoundL After
```
After "P", it is always the case that once "R" becomes satisfied, it holds for at least "5" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ < 5;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/DurationBoundLPattern_After_0.svg)



### DurationBoundL Between
```
Between "P" and "Q", it is always the case that once "R" becomes satisfied, it holds for at least "5" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < 5;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/DurationBoundLPattern_Between_0.svg)



### DurationBoundL AfterUntil
```
After "P" until "Q", it is always the case that once "R" becomes satisfied, it holds for at least "5" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < 5;⌈(!Q && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/DurationBoundLPattern_AfterUntil_0.svg)


