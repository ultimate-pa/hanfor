<!-- Auto generated file, do not make any changes here. -->

## TriggerResponseDelayBoundL1

### TriggerResponseDelayBoundL1 Globally
```
Globally, it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds after at most "10" time units
```

#### Countertraces
```
true;⌈R⌉ ∧ ℓ ≥ 5;⌈(R && (S && !T))⌉;⌈!T⌉ ∧ ℓ > 10;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseDelayBoundL1Pattern_Globally_0.svg)

??? Example "Positive Examples: TriggerResponseDelayBoundL1 - Globally"
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_Globally_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_Globally_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_Globally_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_Globally_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_Globally_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_Globally_5.svg){ loading=lazy width=47% align=left }


### TriggerResponseDelayBoundL1 Before
```
Before "P", it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds after at most "10" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ 5;⌈(!P && (R && (S && !T)))⌉;⌈(!P && !T)⌉ ∧ ℓ > 10;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseDelayBoundL1Pattern_Before_0.svg)



### TriggerResponseDelayBoundL1 After
```
After "P", it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds after at most "10" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ 5;⌈(R && (S && !T))⌉;⌈!T⌉ ∧ ℓ > 10;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseDelayBoundL1Pattern_After_0.svg)

??? Example "Positive Examples: TriggerResponseDelayBoundL1 - After"
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_After_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_After_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_After_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_After_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_After_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_After_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_After_7.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_After_8.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_After_9.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_After_10.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_After_11.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_After_12.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_After_13.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_After_14.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseDelayBoundL1Pattern_After_15.svg){ loading=lazy width=47% align=left }


### TriggerResponseDelayBoundL1 Between
```
Between "P" and "Q", it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds after at most "10" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && (R && (S && !T)))⌉;⌈(!Q && !T)⌉ ∧ ℓ > 10;true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseDelayBoundL1Pattern_Between_0.svg)



### TriggerResponseDelayBoundL1 AfterUntil
```
After "P" until "Q", it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds after at most "10" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && (R && (S && !T)))⌉;⌈(!Q && !T)⌉ ∧ ℓ > 10;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseDelayBoundL1Pattern_AfterUntil_0.svg)


