<!-- Auto generated file, do not make any changes here. -->

## EdgeResponseDelay

### EdgeResponseDelay Globally
```
Globally, it is always the case that once "R" becomes satisfied, "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseDelayPattern_Globally_0.svg)

??? Example "Positive Examples: EdgeResponseDelay - Globally"
    ![](../img/failure_paths/positive/EdgeResponseDelayPattern_Globally_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayPattern_Globally_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayPattern_Globally_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayPattern_Globally_3.svg){ loading=lazy width=47% align=left }


### EdgeResponseDelay Before
```
Before "P", it is always the case that once "R" becomes satisfied, "S" holds after at most "5" time units
```

#### Countertraces
```
⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseDelayPattern_Before_0.svg)



### EdgeResponseDelay After
```
After "P", it is always the case that once "R" becomes satisfied, "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈P⌉;true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseDelayPattern_After_0.svg)

??? Example "Positive Examples: EdgeResponseDelay - After"
    ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_3.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_4.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_5.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/EdgeResponseDelayPattern_After_6.svg){ loading=lazy width=47% align=left }


### EdgeResponseDelay Between
```
Between "P" and "Q", it is always the case that once "R" becomes satisfied, "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > 5;true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseDelayPattern_Between_0.svg)



### EdgeResponseDelay AfterUntil
```
After "P" until "Q", it is always the case that once "R" becomes satisfied, "S" holds after at most "5" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > 5;true
```

#### Phase Event Automata
![](../img/patterns/EdgeResponseDelayPattern_AfterUntil_0.svg)


