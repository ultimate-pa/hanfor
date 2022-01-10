<!-- Auto generated file, do not make any changes here. -->

## EdgeResponseDelayBoundL2

### EdgeResponseDelayBoundL2 Globally
```
Globally, it is always the case that once "R" becomes satisfied, "S" holds after at most "5" time units for at least "10" time units
```

#### Countertraces
```
true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > 5;true
true;⌈!R⌉;⌈R⌉;⌈true⌉ ∧ ℓ < 5;⌈S⌉ ∧ ℓ < 10;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseDelayBoundL2Pattern_Globally_0.svg)
![](../img/patterns/EdgeResponseDelayBoundL2Pattern_Globally_1.svg)

??? Example "Positive Examples: EdgeResponseDelayBoundL2 - Globally"
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_Globally_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_Globally_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_Globally_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_Globally_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_Globally_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_Globally_5.svg){ loading=lazy width=47% align=left }


### EdgeResponseDelayBoundL2 Before
```
Before "P", it is always the case that once "R" becomes satisfied, "S" holds after at most "5" time units for at least "10" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > 5;true
⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉;⌈!P⌉ ∧ ℓ < 5;⌈(!P && S)⌉ ∧ ℓ < 10;⌈(!P && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseDelayBoundL2Pattern_Before_0.svg)
![](../img/patterns/EdgeResponseDelayBoundL2Pattern_Before_1.svg)

??? Example "Positive Examples: EdgeResponseDelayBoundL2 - Before"
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_Before_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_Before_1.svg){ loading=lazy width=47% align=left }


### EdgeResponseDelayBoundL2 After
```
After "P", it is always the case that once "R" becomes satisfied, "S" holds after at most "5" time units for at least "10" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > 5;true
true;⌈P⌉;true;⌈!R⌉;⌈R⌉;⌈true⌉ ∧ ℓ < 5;⌈S⌉ ∧ ℓ < 10;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseDelayBoundL2Pattern_After_0.svg)
![](../img/patterns/EdgeResponseDelayBoundL2Pattern_After_1.svg)

??? Example "Positive Examples: EdgeResponseDelayBoundL2 - After"
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_7.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_8.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_9.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_10.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_11.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_12.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_13.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_14.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_15.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_16.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_17.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_18.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_After_19.svg){ loading=lazy width=47% align=left }


### EdgeResponseDelayBoundL2 Between
```
Between "P" and "Q", it is always the case that once "R" becomes satisfied, "S" holds after at most "5" time units for at least "10" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > 5;true;⌈Q⌉;true
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < 5;⌈(!Q && S)⌉ ∧ ℓ < 10;⌈(!Q && !S)⌉;true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseDelayBoundL2Pattern_Between_0.svg)
![](../img/patterns/EdgeResponseDelayBoundL2Pattern_Between_1.svg)



### EdgeResponseDelayBoundL2 AfterUntil
```
After "P" until "Q", it is always the case that once "R" becomes satisfied, "S" holds after at most "5" time units for at least "10" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > 5;true
true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < 5;⌈(!Q && S)⌉ ∧ ℓ < 10;⌈(!Q && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseDelayBoundL2Pattern_AfterUntil_0.svg)
![](../img/patterns/EdgeResponseDelayBoundL2Pattern_AfterUntil_1.svg)

??? Example "Positive Examples: EdgeResponseDelayBoundL2 - AfterUntil"
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_AfterUntil_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayBoundL2Pattern_AfterUntil_3.svg){ loading=lazy width=47% align=left }

