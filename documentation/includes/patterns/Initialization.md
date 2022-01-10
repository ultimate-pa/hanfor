<!-- Auto generated file, do not make any changes here. -->

## Initialization

### Initialization Globally
```
Globally, it is always the case that initially "R" holds
```

#### Countertraces
```
⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/InitializationPattern_Globally_0.svg)



### Initialization Before
```
Before "P", it is always the case that initially "R" holds
```

#### Countertraces
```
⌈(!P && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/InitializationPattern_Before_0.svg)



### Initialization After
```
After "P", it is always the case that initially "R" holds
```

#### Countertraces
```
true;⌈P⌉;⌈!R⌉;true
```

#### Phase Event Automata
![](../img/patterns/InitializationPattern_After_0.svg)

??? Example "Positive Examples: Initialization - After"
    ![](../img/failure_paths/positive/InitializationPattern_After_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InitializationPattern_After_1.svg){ loading=lazy width=47% align=left }


### Initialization Between
```
Between "P" and "Q", it is always the case that initially "R" holds
```

#### Countertraces
```
true;⌈(P && !Q)⌉;⌈(!Q && !R)⌉;true;⌈Q⌉;true
```

#### Phase Event Automata
![](../img/patterns/InitializationPattern_Between_0.svg)

??? Example "Positive Examples: Initialization - Between"
    ![](../img/failure_paths/positive/InitializationPattern_Between_0.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InitializationPattern_Between_1.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InitializationPattern_Between_2.svg){ loading=lazy width=47% align=left }
    ![](../img/failure_paths/positive/InitializationPattern_Between_3.svg){ loading=lazy width=47% align=left }


### Initialization AfterUntil
```
After "P" until "Q", it is always the case that initially "R" holds
```

#### Countertraces
```
true;⌈P⌉;⌈(!Q && !R)⌉;true
```

#### Phase Event Automata
![](../img/patterns/InitializationPattern_AfterUntil_0.svg)

??? Example "Positive Examples: Initialization - AfterUntil"
    ![](../img/failure_paths/positive/InitializationPattern_AfterUntil_0.svg){ loading=lazy width=47% align=left }

