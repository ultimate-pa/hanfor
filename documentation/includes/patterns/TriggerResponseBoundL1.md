<!-- Auto generated file, do not make any changes here. -->

## TriggerResponseBoundL1

### TriggerResponseBoundL1 Globally
```
Globally, it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds
```

#### Countertraces
```
true;⌈R⌉ ∧ ℓ ≥ 5;⌈(R && (S && !T))⌉;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseBoundL1Pattern_Globally_0.svg)

??? Example "Positive Examples: TriggerResponseBoundL1 - Globally"
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_Globally_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_Globally_1.svg){ loading=lazy width=47% align=left }


### TriggerResponseBoundL1 Before
```
Before "P", it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ 5;⌈(!P && (R && (S && !T)))⌉;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseBoundL1Pattern_Before_0.svg)

??? Example "Positive Examples: TriggerResponseBoundL1 - Before"
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_Before_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_Before_1.svg){ loading=lazy width=47% align=left }


### TriggerResponseBoundL1 After
```
After "P", it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ 5;⌈(R && (S && !T))⌉;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseBoundL1Pattern_After_0.svg)

??? Example "Positive Examples: TriggerResponseBoundL1 - After"
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_After_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_After_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_After_3.svg){ loading=lazy width=47% align=left }


### TriggerResponseBoundL1 Between
```
Between "P" and "Q", it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && (R && (S && !T)))⌉;true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseBoundL1Pattern_Between_0.svg)

??? Example "Positive Examples: TriggerResponseBoundL1 - Between"
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_Between_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_Between_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_Between_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_Between_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_Between_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_Between_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_Between_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_Between_7.svg){ loading=lazy width=47% align=left }


### TriggerResponseBoundL1 AfterUntil
```
After "P" until "Q", it is always the case that after "R" holds for at least "5" time units and "S" holds, then "T" holds
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && (R && (S && !T)))⌉;true
```

#### Phase Event Automata
![](../img/patterns/TriggerResponseBoundL1Pattern_AfterUntil_0.svg)

??? Example "Positive Examples: TriggerResponseBoundL1 - AfterUntil"
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_AfterUntil_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/TriggerResponseBoundL1Pattern_AfterUntil_3.svg){ loading=lazy width=47% align=left }

