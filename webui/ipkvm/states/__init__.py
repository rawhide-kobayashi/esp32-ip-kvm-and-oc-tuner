from . import states

model = states.Overclocking()
machine = states.MyMachine(model, states=states.State, initial=model.state)

machine.get_graph().draw('my_state_diagram.svg', prog='dot')