<!-- Auto generated file, do not make any changes here. -->

## ResponseBoundL12

### ResponseBoundL12 Globally
```
Globally, it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards for at least "10" time units
```

#### Countertraces
```
true;⌈R⌉ ∧ ℓ ≥ 5;⌈S⌉ ∧ ℓ <₀ 10;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL12Pattern_Globally_0.svg)

??? Example "Positive Examples: ResponseBoundL12 - Globally"
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_Globally_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_Globally_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_Globally_2.svg){ loading=lazy width=47% align=left }


### ResponseBoundL12 Before
```
Before "P", it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards for at least "10" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ 5;⌈(!P && S)⌉ ∧ ℓ <₀ 10;⌈(!P && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL12Pattern_Before_0.svg)

??? Example "Positive Examples: ResponseBoundL12 - Before"
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_Before_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_Before_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_Before_2.svg){ loading=lazy width=47% align=left }


### ResponseBoundL12 After
```
After "P", it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards for at least "10" time units
```

#### Countertraces
```
true;⌈P⌉;⌈R⌉ ∧ ℓ ≥ 5;⌈S⌉ ∧ ℓ <₀ 10;⌈!S⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL12Pattern_After_0.svg)

??? Example "Positive Examples: ResponseBoundL12 - After"
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_After_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_After_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_After_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_After_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_After_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_After_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_After_7.svg){ loading=lazy width=47% align=left }


### ResponseBoundL12 Between
```
Between "P" and "Q", it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards for at least "10" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && S)⌉ ∧ ℓ <₀ 10;⌈(!Q && !S)⌉;true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL12Pattern_Between_0.svg)



### ResponseBoundL12 AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds for at least "5" time units, then "S" holds afterwards for at least "10" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈(!Q && S)⌉ ∧ ℓ <₀ 10;⌈(!Q && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseBoundL12Pattern_AfterUntil_0.svg)

??? Example "Positive Examples: ResponseBoundL12 - AfterUntil"
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_AfterUntil_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_AfterUntil_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_AfterUntil_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseBoundL12Pattern_AfterUntil_5.svg){ loading=lazy width=47% align=left }

