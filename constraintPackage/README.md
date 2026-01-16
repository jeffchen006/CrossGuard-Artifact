### Constraint Learning Engine

## Invariants for Cross Contracts:
Key things: Re-entrancy! Cross-Contract Re-entrancy and Read-only Re-entrancy!


Invariant 1: functions cannot be called twice in a single transaction.
We need to define a very specific type of function.
How to infer that?

Invariant 2: A storage slot cannot be increased or decreased at the same time. 

Invariant 3: Transfers cannot happen in two directions in a transaction. 
+ amount checks. 
difference. 

Invariant 4: external calls of traget functions should be limited in a transaction. 

The key idea here is, a victim contract accessed an external contract whose state could be manipulated by the attacker. We try our best to protect it. 




The learning engine starts with a set of benign training inputs.

It infers safety constraints from the training inputs.

Safety constraints define the comfort zone of the application.


