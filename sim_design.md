# notes on the sim module design

## Api
```py
sim = Simulation(inputs=['a:1','b:1','c_in:1'], outputs=['s:1,c:1'], name="full adder")
sim.add_gate(Gate.XOR, "a", "b") # if gate is left unamed the net will named eg. xor0
sim.add_gate(Gate.AND, "a", "b", "carry_a") # named net
sim.add_gate(Gate.XOR, "xor0", "c_in", "s") # specifies that the output of this gate is the output s
sim.add_gate(gate.AND, "xor0", "c_in", "carry_b")
sim.add_gate(gate.OR, "carry_a", "carry_b", "c") # takes the two named nets and outputs to c
print(sim.run({"a": true, "b": true, "c_in": false})) # {"s": false, "c": true}
```
Net may be used in n inputs, if a net is writen by more than 1 gate, it's an error for their state to disagree (conflict)
a switch which outputs either self or `x` should be used in such scenarios to deconflict a net.

