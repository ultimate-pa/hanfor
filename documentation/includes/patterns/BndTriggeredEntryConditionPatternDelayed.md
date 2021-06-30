<!-- Auto generated file, do not make any changes here. -->

## BndTriggeredEntryConditionPatternDelayed

### BndTriggeredEntryConditionPatternDelayed Globally
```
Globally, it is always the case that after "S" holds for at least "5" time units and "R" holds, then "Q" holds after at most "10" time units
```

#### Countertraces
```
true;⌈Q⌉ ∧ ℓ ≥ 5;⌈(Q && R)⌉;⌈!S⌉ ∧ ℓ > 10;true
```

#### Phase Event Automata
![](../img/patterns/BndTriggeredEntryConditionPatternDelayed_Globally_0.svg)

#### Examples


