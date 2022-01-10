<!-- Auto generated file, do not make any changes here. -->

## DurationBoundU

### DurationBoundU Globally
```
Globally, it is always the case that once "R" becomes satisfied, it holds for less than "5" time units
```

#### Countertraces
```
true;⌈R⌉ ∧ ℓ ≥ 5;true
```

#### Phase Event Automata
![](../img/patterns/DurationBoundUPattern_Globally_0.svg)

??? Example "Positive Examples: DurationBoundU - Globally"
    ![](../img/failure_paths/positive/DurationBoundUPattern_Globally_0.svg){ loading=lazy width=47% align=left }


### DurationBoundU Before
```
Before "P", it is always the case that once "R" becomes satisfied, it holds for less than "5" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ 5;true
```

#### Phase Event Automata
![](../img/patterns/DurationBoundUPattern_Before_0.svg)

??? Example "Positive Examples: DurationBoundU - Before"
    ![](../img/failure_paths/positive/DurationBoundUPattern_Before_0.svg){ loading=lazy width=47% align=left }


### DurationBoundU After
```
After "P", it is always the case that once "R" becomes satisfied, it holds for less than "5" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ 5;true
```

#### Phase Event Automata
![](../img/patterns/DurationBoundUPattern_After_0.svg)

??? Example "Positive Examples: DurationBoundU - After"
    ![](../img/failure_paths/positive/DurationBoundUPattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/DurationBoundUPattern_After_1.svg){ loading=lazy width=47% align=left }


### DurationBoundU Between
```
Between "P" and "Q", it is always the case that once "R" becomes satisfied, it holds for less than "5" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/DurationBoundUPattern_Between_0.svg)

??? Example "Positive Examples: DurationBoundU - Between"
    ![](../img/failure_paths/positive/DurationBoundUPattern_Between_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/DurationBoundUPattern_Between_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/DurationBoundUPattern_Between_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/DurationBoundUPattern_Between_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/DurationBoundUPattern_Between_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/DurationBoundUPattern_Between_5.svg){ loading=lazy width=47% align=left }


### DurationBoundU AfterUntil
```
After "P" until "Q", it is always the case that once "R" becomes satisfied, it holds for less than "5" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ 5;true
```

#### Phase Event Automata
![](../img/patterns/DurationBoundUPattern_AfterUntil_0.svg)

??? Example "Positive Examples: DurationBoundU - AfterUntil"
    ![](../img/failure_paths/positive/DurationBoundUPattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/DurationBoundUPattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }

