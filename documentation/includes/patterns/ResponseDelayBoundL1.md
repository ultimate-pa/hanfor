<!-- Auto generated file, do not make any changes here. -->

## ResponseDelayBoundL1

### ResponseDelayBoundL1 Globally
```
Globally, it is always the case that if "R" holds for at least "5" time units, then "S" holds after at most "10" time units
```

#### Countertraces
```
true;⌈R⌉ ∧ ℓ ≥ 5;⌈!S⌉ ∧ ℓ > 10;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayBoundL1Pattern_Globally_0.svg)

??? Example "Positive Examples: ResponseDelayBoundL1 - Globally"
    ![](../img/failure_paths/positive/ResponseDelayBoundL1Pattern_Globally_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL1Pattern_Globally_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL1Pattern_Globally_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL1Pattern_Globally_3.svg){ loading=lazy width=47% align=left }


### ResponseDelayBoundL1 Before
```
Before "P", it is always the case that if "R" holds for at least "5" time units, then "S" holds after at most "10" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ 5;⌈(!P && !S)⌉ ∧ ℓ > 10;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayBoundL1Pattern_Before_0.svg)



### ResponseDelayBoundL1 After
```
After "P", it is always the case that if "R" holds for at least "5" time units, then "S" holds after at most "10" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ 5;⌈!S⌉ ∧ ℓ > 10;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayBoundL1Pattern_After_0.svg)

??? Example "Positive Examples: ResponseDelayBoundL1 - After"
    ![](../img/failure_paths/positive/ResponseDelayBoundL1Pattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL1Pattern_After_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL1Pattern_After_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL1Pattern_After_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL1Pattern_After_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL1Pattern_After_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL1Pattern_After_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL1Pattern_After_7.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL1Pattern_After_8.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL1Pattern_After_9.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL1Pattern_After_10.svg){ loading=lazy width=47% align=left }


### ResponseDelayBoundL1 Between
```
Between "P" and "Q", it is always the case that if "R" holds for at least "5" time units, then "S" holds after at most "10" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && !S)⌉ ∧ ℓ > 10;true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayBoundL1Pattern_Between_0.svg)



### ResponseDelayBoundL1 AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds for at least "5" time units, then "S" holds after at most "10" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && !S)⌉ ∧ ℓ > 10;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayBoundL1Pattern_AfterUntil_0.svg)


