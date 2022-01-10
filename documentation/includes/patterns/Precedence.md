<!-- Auto generated file, do not make any changes here. -->

## Precedence

### Precedence Globally
```
Globally, it is always the case that if "R" holds, then "S" previously held
```

#### Countertraces
```
⌈!S⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedencePattern_Globally_0.svg)

??? Example "Positive Examples: Precedence - Globally"
    ![](../img/failure_paths/positive/PrecedencePattern_Globally_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedencePattern_Globally_1.svg){ loading=lazy width=47% align=left }


### Precedence Before
```
Before "P", it is always the case that if "R" holds, then "S" previously held
```

#### Countertraces
```
⌈(!P && !S)⌉;⌈(!P && R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedencePattern_Before_0.svg)

??? Example "Positive Examples: Precedence - Before"
    ![](../img/failure_paths/positive/PrecedencePattern_Before_0.svg){ loading=lazy width=47% align=left }


### Precedence After
```
After "P", it is always the case that if "R" holds, then "S" previously held
```

#### Countertraces
```
true;⌈P⌉;⌈!S⌉;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedencePattern_After_0.svg)

??? Example "Positive Examples: Precedence - After"
    ![](../img/failure_paths/positive/PrecedencePattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedencePattern_After_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedencePattern_After_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedencePattern_After_3.svg){ loading=lazy width=47% align=left }


### Precedence Between
```
Between "P" and "Q", it is always the case that if "R" holds, then "S" previously held
```

#### Countertraces
```
true;⌈(P && (!Q && !S))⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedencePattern_Between_0.svg)

??? Example "Positive Examples: Precedence - Between"
    ![](../img/failure_paths/positive/PrecedencePattern_Between_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedencePattern_Between_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedencePattern_Between_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedencePattern_Between_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedencePattern_Between_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedencePattern_Between_5.svg){ loading=lazy width=47% align=left }


### Precedence AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then "S" previously held
```

#### Countertraces
```
true;⌈P⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/PrecedencePattern_AfterUntil_0.svg)

??? Example "Positive Examples: Precedence - AfterUntil"
    ![](../img/failure_paths/positive/PrecedencePattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/PrecedencePattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }

