<!-- Auto generated file, do not make any changes here. -->

## EdgeResponseBoundL2

### EdgeResponseBoundL2 Globally
```
Globally, it is always the case that once "R" becomes satisfied, "S" holds for at least "5" time units
```

#### Countertraces
```
true;⌈!R⌉;⌈R⌉;⌈S⌉ ∧ ℓ < 5;⌈!S⌉;true
true;⌈!R⌉;⌈(R && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseBoundL2Pattern_Globally_0.svg)
![](../img/patterns/EdgeResponseBoundL2Pattern_Globally_1.svg)

??? Example "Positive Examples: EdgeResponseBoundL2 - Globally"
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_Globally_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_Globally_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_Globally_2.svg){ loading=lazy width=47% align=left }


### EdgeResponseBoundL2 Before
```
Before "P", it is always the case that once "R" becomes satisfied, "S" holds for at least "5" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉;⌈(!P && S)⌉ ∧ ℓ < 5;⌈(!P && !S)⌉;true
⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && (R && !S))⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseBoundL2Pattern_Before_0.svg)
![](../img/patterns/EdgeResponseBoundL2Pattern_Before_1.svg)

??? Example "Positive Examples: EdgeResponseBoundL2 - Before"
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_Before_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_Before_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_Before_2.svg){ loading=lazy width=47% align=left }


### EdgeResponseBoundL2 After
```
After "P", it is always the case that once "R" becomes satisfied, "S" holds for at least "5" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈!R⌉;⌈R⌉;⌈S⌉ ∧ ℓ < 5;⌈!S⌉;true
true;⌈P⌉;true;⌈!R⌉;⌈(R && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseBoundL2Pattern_After_0.svg)
![](../img/patterns/EdgeResponseBoundL2Pattern_After_1.svg)

??? Example "Positive Examples: EdgeResponseBoundL2 - After"
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_After_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_After_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_After_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_After_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_After_5.svg){ loading=lazy width=47% align=left }


### EdgeResponseBoundL2 Between
```
Between "P" and "Q", it is always the case that once "R" becomes satisfied, "S" holds for at least "5" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && S)⌉ ∧ ℓ < 5;⌈(!Q && !S)⌉;⌈!Q⌉;⌈Q⌉;true
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseBoundL2Pattern_Between_0.svg)
![](../img/patterns/EdgeResponseBoundL2Pattern_Between_1.svg)



### EdgeResponseBoundL2 AfterUntil
```
After "P" until "Q", it is always the case that once "R" becomes satisfied, "S" holds for at least "5" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && S)⌉ ∧ ℓ < 5;⌈(!Q && !S)⌉;true
true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseBoundL2Pattern_AfterUntil_0.svg)
![](../img/patterns/EdgeResponseBoundL2Pattern_AfterUntil_1.svg)

??? Example "Positive Examples: EdgeResponseBoundL2 - AfterUntil"
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_AfterUntil_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_AfterUntil_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_AfterUntil_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundL2Pattern_AfterUntil_5.svg){ loading=lazy width=47% align=left }

