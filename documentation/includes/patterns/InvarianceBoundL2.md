<!-- Auto generated file, do not make any changes here. -->

## InvarianceBoundL2

### InvarianceBoundL2 Globally
```
Globally, it is always the case that if "R" holds, then "S" holds for at least "5" time units
```

#### Countertraces
```
true;⌈R⌉;⌈true⌉ ∧ ℓ < 5;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvarianceBoundL2Pattern_Globally_0.svg)

??? Example "Positive Examples: InvarianceBoundL2 - Globally"
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_Globally_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_Globally_1.svg){ loading=lazy width=47% align=left }


### InvarianceBoundL2 Before
```
Before "P", it is always the case that if "R" holds, then "S" holds for at least "5" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉ ∧ ℓ < 5;⌈(!P && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvarianceBoundL2Pattern_Before_0.svg)

??? Example "Positive Examples: InvarianceBoundL2 - Before"
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_Before_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_Before_1.svg){ loading=lazy width=47% align=left }


### InvarianceBoundL2 After
```
After "P", it is always the case that if "R" holds, then "S" holds for at least "5" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉;⌈true⌉ ∧ ℓ < 5;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvarianceBoundL2Pattern_After_0.svg)

??? Example "Positive Examples: InvarianceBoundL2 - After"
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_After_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_After_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_After_3.svg){ loading=lazy width=47% align=left }


### InvarianceBoundL2 Between
```
Between "P" and "Q", it is always the case that if "R" holds, then "S" holds for at least "5" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < 5;⌈(!Q && !S)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvarianceBoundL2Pattern_Between_0.svg)

??? Example "Positive Examples: InvarianceBoundL2 - Between"
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_Between_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_Between_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_Between_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_Between_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_Between_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_Between_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_Between_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_Between_7.svg){ loading=lazy width=47% align=left }


### InvarianceBoundL2 AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then "S" holds for at least "5" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < 5;⌈(!Q && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvarianceBoundL2Pattern_AfterUntil_0.svg)

??? Example "Positive Examples: InvarianceBoundL2 - AfterUntil"
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_AfterUntil_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvarianceBoundL2Pattern_AfterUntil_3.svg){ loading=lazy width=47% align=left }

