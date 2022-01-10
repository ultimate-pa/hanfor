<!-- Auto generated file, do not make any changes here. -->

## ResponseBoundL1

### ResponseBoundL1 Globally
```
Globally, it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards
```

#### Countertraces
```
true;⌈R⌉ ∧ ℓ ≥ 5;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL1Pattern_Globally_0.svg)

??? Example "Positive Examples: ResponseBoundL1 - Globally"
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Globally_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Globally_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Globally_2.svg){ loading=lazy width=47% align=left }


### ResponseBoundL1 Before
```
Before "P", it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ 5;⌈(!P && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL1Pattern_Before_0.svg)

??? Example "Positive Examples: ResponseBoundL1 - Before"
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Before_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Before_1.svg){ loading=lazy width=47% align=left }


### ResponseBoundL1 After
```
After "P", it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ 5;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL1Pattern_After_0.svg)

??? Example "Positive Examples: ResponseBoundL1 - After"
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_After_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_After_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_After_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_After_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_After_5.svg){ loading=lazy width=47% align=left }


### ResponseBoundL1 Between
```
Between "P" and "Q", it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && !S)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL1Pattern_Between_0.svg)

??? Example "Positive Examples: ResponseBoundL1 - Between"
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Between_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Between_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Between_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Between_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Between_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Between_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Between_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Between_7.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Between_8.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Between_9.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Between_10.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_Between_11.svg){ loading=lazy width=47% align=left }


### ResponseBoundL1 AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL1Pattern_AfterUntil_0.svg)

??? Example "Positive Examples: ResponseBoundL1 - AfterUntil"
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_AfterUntil_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL1Pattern_AfterUntil_3.svg){ loading=lazy width=47% align=left }

