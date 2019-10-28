toc_depth: 2

### MinDurationPattern Globally

Globally, it is always the case that once "Q" becomes satisfied, it holds for at least "c0" time units

true;⌈!Q⌉;⌈Q⌉ ∧ ℓ < 50;⌈!Q⌉;true

![](/img/patterns/MinDurationPattern_Globally.svg)
### MinDurationPattern Before

Before "Q", it is always the case that once "R" becomes satisfied, it holds for at least "c0" time units

⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < 50;⌈(!Q && !R)⌉;true

![](/img/patterns/MinDurationPattern_Before.svg)
### MinDurationPattern After

After "Q", it is always the case that once "R" becomes satisfied, it holds for at least "c0" time units

true;⌈Q⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ < 50;⌈!R⌉;true

![](/img/patterns/MinDurationPattern_After.svg)
### MinDurationPattern Between

Between "Q" and "R", it is always the case that once "S" becomes satisfied, it holds for at least "c0" time units

true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !S)⌉;⌈(!R && S)⌉ ∧ ℓ < 50;⌈(!R && !S)⌉;⌈!R⌉;⌈R⌉;true

![](/img/patterns/MinDurationPattern_Between.svg)
### MinDurationPattern AfterUntil

After "Q" until "R", it is always the case that once "S" becomes satisfied, it holds for at least "c0" time units

true;⌈(Q && !R)⌉;⌈!R⌉;⌈(!R && !S)⌉;⌈(!R && S)⌉ ∧ ℓ < 50;⌈(!R && !S)⌉;⌈!R⌉;true

![](/img/patterns/MinDurationPattern_AfterUntil.svg)
