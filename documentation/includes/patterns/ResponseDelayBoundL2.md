<!-- Auto generated file, do not make any changes here. -->

## ResponseDelayBoundL2

### ResponseDelayBoundL2 Globally
```
Globally, it is always the case that if "R" holds, then "S" holds after at most "5" time units for at least "10" time units
```

#### Countertraces
```
true;⌈R⌉;⌈!S⌉ ∧ ℓ > 5;true
true;⌈R⌉;⌈!S⌉ ∧ ℓ <₀ 5;⌈S⌉ ∧ ℓ < 10;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayBoundL2Pattern_Globally_0.svg)
![](../img/patterns/ResponseDelayBoundL2Pattern_Globally_1.svg)

??? Example "Positive Examples: ResponseDelayBoundL2 - Globally"
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_Globally_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_Globally_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_Globally_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_Globally_3.svg){ loading=lazy width=47% align=left }


### ResponseDelayBoundL2 Before
```
Before "P", it is always the case that if "R" holds, then "S" holds after at most "5" time units for at least "10" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉ ∧ ℓ > 5;true
⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉ ∧ ℓ <₀ 5;⌈(!P && S)⌉ ∧ ℓ < 10;⌈(!P && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayBoundL2Pattern_Before_0.svg)
![](../img/patterns/ResponseDelayBoundL2Pattern_Before_1.svg)

??? Example "Positive Examples: ResponseDelayBoundL2 - Before"
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_Before_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_Before_1.svg){ loading=lazy width=47% align=left }


### ResponseDelayBoundL2 After
```
After "P", it is always the case that if "R" holds, then "S" holds after at most "5" time units for at least "10" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉;⌈!S⌉ ∧ ℓ > 5;true
true;⌈P⌉;true;⌈R⌉;⌈!S⌉ ∧ ℓ <₀ 5;⌈S⌉ ∧ ℓ < 10;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayBoundL2Pattern_After_0.svg)
![](../img/patterns/ResponseDelayBoundL2Pattern_After_1.svg)

??? Example "Positive Examples: ResponseDelayBoundL2 - After"
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_After_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_After_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_After_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_After_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_After_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_After_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_After_7.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_After_8.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_After_9.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_After_10.svg){ loading=lazy width=47% align=left }


### ResponseDelayBoundL2 Between
```
Between "P" and "Q", it is always the case that if "R" holds, then "S" holds after at most "5" time units for at least "10" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ > 5;true;⌈Q⌉;true
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ <₀ 5;⌈(!Q && S)⌉ ∧ ℓ < 10;⌈(!Q && !S)⌉;true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayBoundL2Pattern_Between_0.svg)
![](../img/patterns/ResponseDelayBoundL2Pattern_Between_1.svg)



### ResponseDelayBoundL2 AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then "S" holds after at most "5" time units for at least "10" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ > 5;true
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ <₀ 5;⌈(!Q && S)⌉ ∧ ℓ < 10;⌈(!Q && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayBoundL2Pattern_AfterUntil_0.svg)
![](../img/patterns/ResponseDelayBoundL2Pattern_AfterUntil_1.svg)

??? Example "Positive Examples: ResponseDelayBoundL2 - AfterUntil"
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_AfterUntil_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayBoundL2Pattern_AfterUntil_3.svg){ loading=lazy width=47% align=left }

