<!-- Auto generated file, do not make any changes here. -->

## PrecedenceChain12

### PrecedenceChain12 Globally
```
Globally, it is always the case that if "R" holds and is succeeded by "S", then "T" previously held
```

#### Countertraces
```
⌈!T⌉;⌈R⌉;true;⌈S⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedenceChain12Pattern_Globally_0.svg)

??? Example "Positive Examples: PrecedenceChain12 - Globally"
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Globally_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Globally_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Globally_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Globally_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Globally_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Globally_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Globally_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Globally_7.svg){ loading=lazy width=47% align=left }


### PrecedenceChain12 Before
```
Before "P", it is always the case that if "R" holds and is succeeded by "S", then "T" previously held
```

#### Countertraces
```
⌈(!P && !T)⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedenceChain12Pattern_Before_0.svg)

??? Example "Positive Examples: PrecedenceChain12 - Before"
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Before_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Before_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Before_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Before_3.svg){ loading=lazy width=47% align=left }


### PrecedenceChain12 After
```
After "P", it is always the case that if "R" holds and is succeeded by "S", then "T" previously held
```

#### Countertraces
```
true;⌈P⌉;⌈!T⌉;⌈R⌉;true;⌈S⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedenceChain12Pattern_After_0.svg)

??? Example "Positive Examples: PrecedenceChain12 - After"
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_7.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_8.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_9.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_10.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_11.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_12.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_13.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_14.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_15.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_16.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_17.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_After_18.svg){ loading=lazy width=47% align=left }


### PrecedenceChain12 Between
```
Between "P" and "Q", it is always the case that if "R" holds and is succeeded by "S", then "T" previously held
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedenceChain12Pattern_Between_0.svg)

??? Example "Positive Examples: PrecedenceChain12 - Between"
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Between_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Between_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Between_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Between_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Between_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Between_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Between_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Between_7.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Between_8.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Between_9.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Between_10.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Between_11.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Between_12.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Between_13.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Between_14.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_Between_15.svg){ loading=lazy width=47% align=left }


### PrecedenceChain12 AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds and is succeeded by "S", then "T" previously held
```

#### Countertraces
```
true;⌈P⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedenceChain12Pattern_AfterUntil_0.svg)

??? Example "Positive Examples: PrecedenceChain12 - AfterUntil"
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_AfterUntil_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_AfterUntil_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_AfterUntil_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_AfterUntil_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_AfterUntil_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain12Pattern_AfterUntil_7.svg){ loading=lazy width=47% align=left }

