<!-- Auto generated file, do not make any changes here. -->

## Invariance

### Invariance Globally
```
Globally, it is always the case that if "R" holds, then "S" holds as well
```

#### Countertraces
```
true;⌈(R && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvariancePattern_Globally_0.svg)

??? Example "Positive Examples: Invariance - Globally"
    ![](../img/failure_paths/positive/InvariancePattern_Globally_0.svg){ loading=lazy width=47% align=left }


### Invariance Before
```
Before "P", it is always the case that if "R" holds, then "S" holds as well
```

#### Countertraces
```
⌈!P⌉;⌈(!P && (R && !S))⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvariancePattern_Before_0.svg)

??? Example "Positive Examples: Invariance - Before"
    ![](../img/failure_paths/positive/InvariancePattern_Before_0.svg){ loading=lazy width=47% align=left }


### Invariance After
```
After "P", it is always the case that if "R" holds, then "S" holds as well
```

#### Countertraces
```
true;⌈P⌉;true;⌈(R && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvariancePattern_After_0.svg)

??? Example "Positive Examples: Invariance - After"
    ![](../img/failure_paths/positive/InvariancePattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvariancePattern_After_1.svg){ loading=lazy width=47% align=left }


### Invariance Between
```
Between "P" and "Q", it is always the case that if "R" holds, then "S" holds as well
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvariancePattern_Between_0.svg)

??? Example "Positive Examples: Invariance - Between"
    ![](../img/failure_paths/positive/InvariancePattern_Between_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvariancePattern_Between_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvariancePattern_Between_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvariancePattern_Between_3.svg){ loading=lazy width=47% align=left }


### Invariance AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then "S" holds as well
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;true
```

#### Phase Event Automata
![](../img/patterns/InvariancePattern_AfterUntil_0.svg)

??? Example "Positive Examples: Invariance - AfterUntil"
    ![](../img/failure_paths/positive/InvariancePattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InvariancePattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }

