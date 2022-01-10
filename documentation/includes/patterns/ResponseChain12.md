<!-- Auto generated file, do not make any changes here. -->

## ResponseChain12

### ResponseChain12 Before
```
Before "P", it is always the case that if "R" holds, then "S" eventually holds and is succeeded by "T"
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉;⌈P⌉;true
⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;⌈(!P && !T)⌉;⌈P⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseChain12Pattern_Before_0.svg)
![](../img/patterns/ResponseChain12Pattern_Before_1.svg)

??? Example "Positive Examples: ResponseChain12 - Before"
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Before_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Before_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Before_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Before_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Before_4.svg){ loading=lazy width=47% align=left }


### ResponseChain12 Between
```
Between "P" and "Q", it is always the case that if "R" holds, then "S" eventually holds and is succeeded by "T"
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉;⌈Q⌉;true
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseChain12Pattern_Between_0.svg)
![](../img/patterns/ResponseChain12Pattern_Between_1.svg)

??? Example "Positive Examples: ResponseChain12 - Between"
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Between_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Between_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Between_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Between_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Between_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Between_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Between_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Between_7.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Between_8.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Between_9.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Between_10.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_Between_11.svg){ loading=lazy width=47% align=left }


### ResponseChain12 AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then "S" eventually holds and is succeeded by "T"
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉;⌈Q⌉;true
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseChain12Pattern_AfterUntil_0.svg)
![](../img/patterns/ResponseChain12Pattern_AfterUntil_1.svg)

??? Example "Positive Examples: ResponseChain12 - AfterUntil"
    ![](../img/failure_paths/positive/ResponseChain12Pattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_AfterUntil_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_AfterUntil_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_AfterUntil_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_AfterUntil_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_AfterUntil_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_AfterUntil_7.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_AfterUntil_8.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_AfterUntil_9.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_AfterUntil_10.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseChain12Pattern_AfterUntil_11.svg){ loading=lazy width=47% align=left }

