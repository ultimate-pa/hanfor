<!-- Auto generated file, do not make any changes here. -->

## Response

### Response Before
```
Before "P", it is always the case that if "R" holds, then "S" eventually holds
```

#### Countertraces
```
⌈!P⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉;⌈P⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponsePattern_Before_0.svg)

??? Example "Positive Examples: Response - Before"
    ![](../img/failure_paths/positive/ResponsePattern_Before_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponsePattern_Before_1.svg){ loading=lazy width=47% align=left }
??? Example "Negative Examples: Response - Before"
    ![](../img/failure_paths/negative/ResponsePattern_Before_0.svg){ loading=lazy width=47% align=left }


### Response Between
```
Between "P" and "Q", it is always the case that if "R" holds, then "S" eventually holds
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponsePattern_Between_0.svg)

??? Example "Positive Examples: Response - Between"
    ![](../img/failure_paths/positive/ResponsePattern_Between_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponsePattern_Between_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponsePattern_Between_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponsePattern_Between_3.svg){ loading=lazy width=47% align=left }
??? Example "Negative Examples: Response - Between"
    ![](../img/failure_paths/negative/ResponsePattern_Between_0.svg){ loading=lazy width=47% align=left }


### Response AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then "S" eventually holds
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponsePattern_AfterUntil_0.svg)

??? Example "Positive Examples: Response - AfterUntil"
    ![](../img/failure_paths/positive/ResponsePattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponsePattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponsePattern_AfterUntil_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponsePattern_AfterUntil_3.svg){ loading=lazy width=47% align=left }

