from enum import Enum

from transitions.experimental.utils import with_model_definitions, event, add_transitions, transition
from transitions import Machine


class State(Enum):
    A = "A"
    B = "B"
    C = "C"


class Model:

    state: State = State.A

    @add_transitions(transition(source=State.B, dest=State.A))
    def foo(self): ...

    @add_transitions(transition(source=State.C, dest=State.A))
    def fod(self): ...

    @add_transitions(transition(source=State.A, dest=State.B))
    def fud(self): ...

    bar = event(
        {"source": State.B, "dest": State.A, "conditions": lambda: False},
        transition(source=State.B, dest=State.C)
    )


@with_model_definitions  # don't forget to define your model with this decorator!
class MyMachine(Machine):
    pass


model = Model()
machine = MyMachine(model, states=State, initial=model.state)
print(model.state)
model.fud()
print(model.state)
model.bar()
print(model.state)
assert model.state == State.C
model.fod()
print(model.state)
assert model.state == State.A