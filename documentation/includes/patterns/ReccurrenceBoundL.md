<!-- Auto generated file, do not make any changes here. -->

## ReccurrenceBoundL

### ReccurrenceBoundL Globally
```
Globally, it is always the case that "R" holds at least every "5" time units
```

#### Countertraces
```
true;⌈!R⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/ReccurrenceBoundLPattern_Globally_0.svg)



### ReccurrenceBoundL Before
```
Before "P", it is always the case that "R" holds at least every "5" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && !R)⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/ReccurrenceBoundLPattern_Before_0.svg)



### ReccurrenceBoundL After
```
After "P", it is always the case that "R" holds at least every "5" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈!R⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/ReccurrenceBoundLPattern_After_0.svg)



### ReccurrenceBoundL Between
```
Between "P" and "Q", it is always the case that "R" holds at least every "5" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > 5;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ReccurrenceBoundLPattern_Between_0.svg)

??? Example "Positive Examples: ReccurrenceBoundL - Between"
    ![](../img/failure_paths/positive/ReccurrenceBoundLPattern_Between_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ReccurrenceBoundLPattern_Between_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ReccurrenceBoundLPattern_Between_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ReccurrenceBoundLPattern_Between_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ReccurrenceBoundLPattern_Between_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ReccurrenceBoundLPattern_Between_5.svg){ loading=lazy width=47% align=left }


### ReccurrenceBoundL AfterUntil
```
After "P" until "Q", it is always the case that "R" holds at least every "5" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/ReccurrenceBoundLPattern_AfterUntil_0.svg)


