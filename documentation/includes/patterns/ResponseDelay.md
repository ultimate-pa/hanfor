<!-- Auto generated file, do not make any changes here. -->

## ResponseDelay

### ResponseDelay Globally
```
Globally, it is always the case that if "R" holds, then "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayPattern_Globally_0.svg)

??? Example "Positive Examples: ResponseDelay - Globally"
    ![](../img/failure_paths/positive/ResponseDelayPattern_Globally_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayPattern_Globally_1.svg){ loading=lazy width=47% align=left }


### ResponseDelay Before
```
Before "P", it is always the case that if "R" holds, then "S" holds after at most "5" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayPattern_Before_0.svg)



### ResponseDelay After
```
After "P", it is always the case that if "R" holds, then "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayPattern_After_0.svg)

??? Example "Positive Examples: ResponseDelay - After"
    ![](../img/failure_paths/positive/ResponseDelayPattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayPattern_After_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayPattern_After_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayPattern_After_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayPattern_After_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayPattern_After_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayPattern_After_6.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/ResponseDelayPattern_After_7.svg){ loading=lazy width=47% align=left }


### ResponseDelay Between
```
Between "P" and "Q", it is always the case that if "R" holds, then "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > 5;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayPattern_Between_0.svg)



### ResponseDelay AfterUntil
```
After "P" until "Q", it is always the case that if "R" holds, then "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/ResponseDelayPattern_AfterUntil_0.svg)


