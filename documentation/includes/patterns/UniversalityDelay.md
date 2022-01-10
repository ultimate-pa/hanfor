<!-- Auto generated file, do not make any changes here. -->

## UniversalityDelay

### UniversalityDelay Globally
```
Globally, it is always the case that "R" holds after at most "5" time units
```

#### Countertraces
```
⌈true⌉ ∧ ℓ ≥ 5;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityDelayPattern_Globally_0.svg)

??? Example "Positive Examples: UniversalityDelay - Globally"
    ![](../img/failure_paths/positive/UniversalityDelayPattern_Globally_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/UniversalityDelayPattern_Globally_1.svg){ loading=lazy width=47% align=left }


### UniversalityDelay Before
```
Before "P", it is always the case that "R" holds after at most "5" time units
```

#### Countertraces
```
⌈!P⌉ ∧ ℓ ≥ 5;⌈(!P && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityDelayPattern_Before_0.svg)

??? Example "Positive Examples: UniversalityDelay - Before"
    ![](../img/failure_paths/positive/UniversalityDelayPattern_Before_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/UniversalityDelayPattern_Before_1.svg){ loading=lazy width=47% align=left }


### UniversalityDelay After
```
After "P", it is always the case that "R" holds after at most "5" time units
```

#### Countertraces
```
true;⌈P⌉;⌈true⌉ ∧ ℓ ≥ 5;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityDelayPattern_After_0.svg)

??? Example "Positive Examples: UniversalityDelay - After"
    ![](../img/failure_paths/positive/UniversalityDelayPattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/UniversalityDelayPattern_After_1.svg){ loading=lazy width=47% align=left }


### UniversalityDelay Between
```
Between "P" and "Q", it is always the case that "R" holds after at most "5" time units
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉ ∧ ℓ ≥ 5;⌈(!Q && !R)⌉;true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityDelayPattern_Between_0.svg)

??? Example "Positive Examples: UniversalityDelay - Between"
    ![](../img/failure_paths/positive/UniversalityDelayPattern_Between_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/UniversalityDelayPattern_Between_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/UniversalityDelayPattern_Between_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/UniversalityDelayPattern_Between_3.svg){ loading=lazy width=47% align=left }


### UniversalityDelay AfterUntil
```
After "P" until "Q", it is always the case that "R" holds after at most "5" time units
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉ ∧ ℓ ≥ 5;⌈(!Q && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityDelayPattern_AfterUntil_0.svg)

??? Example "Positive Examples: UniversalityDelay - AfterUntil"
    ![](../img/failure_paths/positive/UniversalityDelayPattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/UniversalityDelayPattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/UniversalityDelayPattern_AfterUntil_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/UniversalityDelayPattern_AfterUntil_3.svg){ loading=lazy width=47% align=left }

