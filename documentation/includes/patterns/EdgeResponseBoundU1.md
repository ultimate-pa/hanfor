<!-- Auto generated file, do not make any changes here. -->

## EdgeResponseBoundU1

### EdgeResponseBoundU1 Globally
```
Globally, it is always the case that once "R" becomes satisfied and holds for at most "5" time units, then "S" holds afterwards
```

#### Countertraces
```
true;⌈!R⌉;⌈R⌉ ∧ ℓ ≤ 5;⌈(!R && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseBoundU1Pattern_Globally_0.svg)

??? Example "Positive Examples: EdgeResponseBoundU1 - Globally"
    ![](../img/failure_paths/positive/EdgeResponseBoundU1Pattern_Globally_0.svg){ loading=lazy width=47% align=left }


### EdgeResponseBoundU1 Before
```
Before "P", it is always the case that once "R" becomes satisfied and holds for at most "5" time units, then "S" holds afterwards
```

#### Countertraces
```
⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉ ∧ ℓ ≥ 5;⌈(!P && (!R && !S))⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseBoundU1Pattern_Before_0.svg)

??? Example "Positive Examples: EdgeResponseBoundU1 - Before"
    ![](../img/failure_paths/positive/EdgeResponseBoundU1Pattern_Before_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundU1Pattern_Before_1.svg){ loading=lazy width=47% align=left }


### EdgeResponseBoundU1 After
```
After "P", it is always the case that once "R" becomes satisfied and holds for at most "5" time units, then "S" holds afterwards
```

#### Countertraces
```
true;⌈P⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ ≤ 5;⌈(!R && !S)⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseBoundU1Pattern_After_0.svg)

??? Example "Positive Examples: EdgeResponseBoundU1 - After"
    ![](../img/failure_paths/positive/EdgeResponseBoundU1Pattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundU1Pattern_After_1.svg){ loading=lazy width=47% align=left }


### EdgeResponseBoundU1 Between
```
Between "P" and "Q", it is always the case that once "R" becomes satisfied and holds for at most "5" time units, then "S" holds afterwards
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ ≤ 5;⌈(!Q && (!R && !S))⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseBoundU1Pattern_Between_0.svg)

??? Example "Positive Examples: EdgeResponseBoundU1 - Between"
    ![](../img/failure_paths/positive/EdgeResponseBoundU1Pattern_Between_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundU1Pattern_Between_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundU1Pattern_Between_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundU1Pattern_Between_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundU1Pattern_Between_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundU1Pattern_Between_5.svg){ loading=lazy width=47% align=left }


### EdgeResponseBoundU1 AfterUntil
```
After "P" until "Q", it is always the case that once "R" becomes satisfied and holds for at most "5" time units, then "S" holds afterwards
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ ≤ 5;⌈(!Q && (!R && !S))⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseBoundU1Pattern_AfterUntil_0.svg)

??? Example "Positive Examples: EdgeResponseBoundU1 - AfterUntil"
    ![](../img/failure_paths/positive/EdgeResponseBoundU1Pattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseBoundU1Pattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }

