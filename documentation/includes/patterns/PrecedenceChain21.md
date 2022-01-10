<!-- Auto generated file, do not make any changes here. -->

## PrecedenceChain21

### PrecedenceChain21 Globally
```
Globally, it is always the case that if "R" holds, then "S" previously held and was preceded by "T"
```

#### Countertraces
```
⌈!T⌉;⌈R⌉;true
⌈!S⌉;⌈R⌉;true
⌈!T⌉;⌈(S && !T)⌉;⌈!T⌉;⌈(!S && T)⌉;⌈!S⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedenceChain21Pattern_Globally_0.svg)
![](../img/patterns/PrecedenceChain21Pattern_Globally_1.svg)
![](../img/patterns/PrecedenceChain21Pattern_Globally_2.svg)

??? Example "Positive Examples: PrecedenceChain21 - Globally"
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_Globally_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_Globally_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_Globally_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_Globally_3.svg){ loading=lazy width=47% align=left }


### PrecedenceChain21 Before
```
Before "P", it is always the case that if "R" holds, then "S" previously held and was preceded by "T"
```

#### Countertraces
```
⌈(!P && !T)⌉;⌈(!P && R)⌉;true
⌈(!P && !S)⌉;⌈(!P && R)⌉;true
⌈(!P && !T)⌉;⌈(!P && (S && !T))⌉;⌈(!P && !T)⌉;⌈(!P && (!S && T))⌉;⌈(!P && !S)⌉;⌈(!P && R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedenceChain21Pattern_Before_0.svg)
![](../img/patterns/PrecedenceChain21Pattern_Before_1.svg)
![](../img/patterns/PrecedenceChain21Pattern_Before_2.svg)

??? Example "Positive Examples: PrecedenceChain21 - Before"
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_Before_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_Before_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_Before_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_Before_3.svg){ loading=lazy width=47% align=left }


### PrecedenceChain21 After
```
After "P", it is always the case that if "R" holds, then "S" previously held and was preceded by "T"
```

#### Countertraces
```
true;⌈P⌉;⌈!T⌉;⌈R⌉;true
true;⌈P⌉;⌈!S⌉;⌈R⌉;true
true;⌈P⌉;⌈!T⌉;⌈(S && !T)⌉;⌈!T⌉;⌈(!S && T)⌉;⌈!S⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedenceChain21Pattern_After_0.svg)
![](../img/patterns/PrecedenceChain21Pattern_After_1.svg)
![](../img/patterns/PrecedenceChain21Pattern_After_2.svg)

??? Example "Positive Examples: PrecedenceChain21 - After"
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_After_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_After_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_After_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_After_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_After_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_After_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_After_7.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_After_8.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_After_9.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_After_10.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_After_11.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_After_12.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_After_13.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_After_14.svg){ loading=lazy width=47% align=left }


### PrecedenceChain21 Between
```
Between "P" and "Q", it is always the case that if "R" holds, then "S" previously held and was preceded by "T"
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true
true;⌈(P && !Q)⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true
true;⌈(P && !Q)⌉;⌈(!Q && !T)⌉;⌈(!Q && (S && !T))⌉;⌈(!Q && !T)⌉;⌈(!Q && (!S && T))⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedenceChain21Pattern_Between_0.svg)
![](../img/patterns/PrecedenceChain21Pattern_Between_1.svg)
![](../img/patterns/PrecedenceChain21Pattern_Between_2.svg)



### PrecedenceChain21 AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then "S" previously held and was preceded by "T"
```

#### Countertraces
```
true;⌈P⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;true
true;⌈P⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;true
true;⌈P⌉;⌈(!Q && !T)⌉;⌈(!Q && (S && !T))⌉;⌈(!Q && !T)⌉;⌈(!Q && (!S && T))⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedenceChain21Pattern_AfterUntil_0.svg)
![](../img/patterns/PrecedenceChain21Pattern_AfterUntil_1.svg)
![](../img/patterns/PrecedenceChain21Pattern_AfterUntil_2.svg)

??? Example "Positive Examples: PrecedenceChain21 - AfterUntil"
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_AfterUntil_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_AfterUntil_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_AfterUntil_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_AfterUntil_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_AfterUntil_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_AfterUntil_7.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_AfterUntil_8.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedenceChain21Pattern_AfterUntil_9.svg){ loading=lazy width=47% align=left }

