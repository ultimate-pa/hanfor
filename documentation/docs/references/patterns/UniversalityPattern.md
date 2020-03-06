<!-- Auto generated file, do not make any changes here. -->

## UniversalityPattern

### UniversalityPattern Globally
```
Globally, it is always the case that "Q" holds
```
```
Counterexample Trace: true;⌈!Q⌉;true
```

![](../img/patterns/UniversalityPattern_Globally.svg)


<table class="pattern_examples">
<thead><tr><th>Positive examples</th><th>Negative examples</th></tr></thead>
<tbody>
<tr><td><a data-lightbox="all_images" data-title="" href="../img/failure_paths/UniversalityPattern_Globally_0.svg"><img alt="" src="../img/failure_paths/UniversalityPattern_Globally_0.svg"></a></td><td></td></tr>
</tbody>
</table>


### UniversalityPattern Before
```
Before "Q", it is always the case that "R" holds
```
```
Counterexample Trace: ⌈!Q⌉;⌈(!Q && !R)⌉;true
```

![](../img/patterns/UniversalityPattern_Before.svg)

![](../img/failure_paths/UniversalityPattern_Before_0.svg)


### UniversalityPattern After
```
After "Q", it is always the case that "R" holds
```
```
Counterexample Trace: true;⌈Q⌉;true;⌈!R⌉;true
```

![](../img/patterns/UniversalityPattern_After.svg)

![](../img/failure_paths/UniversalityPattern_After_0.svg)


### UniversalityPattern Between
```
Between "Q" and "R", it is always the case that "S" holds
```
```
Counterexample Trace: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !S)⌉;⌈!R⌉;⌈R⌉;true
```

![](../img/patterns/UniversalityPattern_Between.svg)


### UniversalityPattern AfterUntil
```
After "Q" until "R", it is always the case that "S" holds
```
```
Counterexample Trace: true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !S)⌉;true
```

![](../img/patterns/UniversalityPattern_AfterUntil.svg)

![](../img/failure_paths/UniversalityPattern_AfterUntil_0.svg)

