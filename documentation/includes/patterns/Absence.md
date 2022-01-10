<!-- Auto generated file, do not make any changes here. -->

## Absence

### Absence Globally
```
Globally, it is never the case that "R" holds
```

#### Countertraces
```
true;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/AbsencePattern_Globally_0.svg)

??? Example "Positive Examples: Absence - Globally"
    ![](../img/failure_paths/positive/AbsencePattern_Globally_0.svg){ loading=lazy width=47% align=left }


### Absence Before
```
Before "P", it is never the case that "R" holds
```

#### Countertraces
```
⌈!P⌉;⌈(!P && R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/AbsencePattern_Before_0.svg)

??? Example "Positive Examples: Absence - Before"
    ![](../img/failure_paths/positive/AbsencePattern_Before_0.svg){ loading=lazy width=47% align=left }


### Absence After
```
After "P", it is never the case that "R" holds
```

#### Countertraces
```
true;⌈P⌉;true;⌈R⌉;true
```

#### Phase Event Automata
![](../img/patterns/AbsencePattern_After_0.svg)

??? Example "Positive Examples: Absence - After"
    ![](../img/failure_paths/positive/AbsencePattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/AbsencePattern_After_1.svg){ loading=lazy width=47% align=left }


### Absence Between
```
Between "P" and "Q", it is never the case that "R" holds
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/AbsencePattern_Between_0.svg)

??? Example "Positive Examples: Absence - Between"
    ![](../img/failure_paths/positive/AbsencePattern_Between_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/AbsencePattern_Between_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/AbsencePattern_Between_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/AbsencePattern_Between_3.svg){ loading=lazy width=47% align=left }


### Absence AfterUntil
```
After "P" until "Q", it is never the case that "R" holds
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/AbsencePattern_AfterUntil_0.svg)

??? Example "Positive Examples: Absence - AfterUntil"
    ![](../img/failure_paths/positive/AbsencePattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/AbsencePattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }

