<!-- Auto generated file, do not make any changes here. -->

## Universality

### Universality Globally
```
Globally, it is always the case that "R" holds
```

#### Countertraces
```
true;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityPattern_Globally_0.svg)

??? Example "Positive Examples: Universality - Globally"
    ![](../img/failure_paths/positive/UniversalityPattern_Globally_0.svg){ loading=lazy width=47% align=left }
??? Example "Negative Examples: Universality - Globally"
    ![](../img/failure_paths/negative/UniversalityPattern_Globally_0.svg){ loading=lazy width=47% align=left }



### Universality Before
```
Before "P", it is always the case that "R" holds
```

#### Countertraces
```
⌈!P⌉;⌈(!P && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityPattern_Before_0.svg)

??? Example "Positive Examples: Universality - Before"
    ![](../img/failure_paths/positive/UniversalityPattern_Before_0.svg){ loading=lazy width=47% align=left }
??? Example "Negative Examples: Universality - Before"
    ![](../img/failure_paths/negative/UniversalityPattern_Before_0.svg){ loading=lazy width=47% align=left }


### Universality After
```
After "P", it is always the case that "R" holds
```

#### Countertraces
```
true;⌈P⌉;true;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityPattern_After_0.svg)

??? Example "Positive Examples: Universality - After"
    ![](../img/failure_paths/positive/UniversalityPattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/UniversalityPattern_After_1.svg){ loading=lazy width=47% align=left }
??? Example "Negative Examples: Universality - After"
    ![](../img/failure_paths/negative/UniversalityPattern_After_0.svg){ loading=lazy width=47% align=left }


### Universality Between
```
Between "P" and "Q", it is always the case that "R" holds
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityPattern_Between_0.svg)

??? Example "Positive Examples: Universality - Between"
    ![](../img/failure_paths/positive/UniversalityPattern_Between_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/UniversalityPattern_Between_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/UniversalityPattern_Between_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/UniversalityPattern_Between_3.svg){ loading=lazy width=47% align=left }
??? Example "Negative Examples: Universality - Between"
    ![](../img/failure_paths/negative/UniversalityPattern_Between_0.svg){ loading=lazy width=47% align=left }


### Universality AfterUntil
```
After "P" until "Q", it is always the case that "R" holds
```

#### Countertraces
```
true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/UniversalityPattern_AfterUntil_0.svg)

??? Example "Positive Examples: Universality - AfterUntil"
    ![](../img/failure_paths/positive/UniversalityPattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/UniversalityPattern_AfterUntil_1.svg){ loading=lazy width=47% align=left }
??? Example "Negative Examples: Universality - AfterUntil"
    ![](../img/failure_paths/negative/UniversalityPattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }

