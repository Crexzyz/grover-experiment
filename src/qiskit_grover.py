import numpy as np
from grover_algorithm import GroverAlgorithm
from qiskit import (
    ClassicalRegister,
    QuantumCircuit,
    QuantumRegister
)

class QiskitGrover(GroverAlgorithm):
    clause_list = [[0,1],[0,2],[1,3],[2,3]]
    
    
    def __init__(self):
        self.value_qubits = 4
        self.clause_number = len(self.clause_list)
        self.result_qubits = QuantumRegister(self.value_qubits, name='r')
        self.clause_qubits = QuantumRegister(self.clause_number, name='c')
        self.output_qubit = QuantumRegister(1, name='out')
        self.cbits = ClassicalRegister(self.value_qubits, name='cbits')
        self.qc = QuantumCircuit(self.result_qubits, self.clause_qubits, self.output_qubit, self.cbits)
        self.known_qubits = {}
        self.unknown_qubits = [x for x in range(self.value_qubits) if x not in self.known_qubits]


    def PrepareStates(self):
        # Initialize 'out0' in state |->
        self.qc.initialize([1, -1]/np.sqrt(2), self.output_qubit)

        # Initialize qubits in state |s>
        for index, var_qubit in enumerate(self.result_qubits):
            if index in self.known_qubits:
                if self.known_qubits[index]:
                    self.qc.x(index)
            if index in self.unknown_qubits:
                self.qc.h(var_qubit)

        self.qc.barrier()


    def Oracle(self):
        # Compute clauses
        i = 0
        for clause in self.clause_list:
            self.XOR(clause[0], clause[1], self.clause_qubits[i])
            i += 1

        # Flip 'output' bit if all clauses are satisfied
        self.qc.mct(self.clause_qubits, self.output_qubit)

        # Uncompute clauses to reset clause-checking bits to 0
        i = 0
        for clause in self.clause_list:
            self.XOR(clause[0], clause[1], self.clause_qubits[i])
            i += 1


    def Diffuser(self):
        diffuser = QuantumCircuit(self.value_qubits)

        # Apply transformation |s> -> |00..0> (H-gates)
        for qubit in self.unknown_qubits:
            diffuser.h(qubit)
        # Apply transformation |00..0> -> |11..1> (X-gates)
        for qubit in self.unknown_qubits:
            diffuser.x(qubit)
        # Do multi-controlled-Z gate
        diffuser.h(self.value_qubits - 1)
        diffuser.mct(self.unknown_qubits[:-1], self.value_qubits - 1)  # multi-controlled-toffoli
        diffuser.h(self.value_qubits - 1)
        # Apply transformation |11..1> -> |00..0>
        for qubit in self.unknown_qubits:
            diffuser.x(qubit)
        # Apply transformation |00..0> -> |s>
        for qubit in self.unknown_qubits:
            diffuser.h(qubit)
        # We will return the diffuser as a gate
        diffuser_gate = diffuser.to_gate()
        diffuser_gate.name = "U$_s$"
        self.qc.append(diffuser_gate, self.unknown_qubits)


    def Measure(self):
        self.qc.measure(self.result_qubits, self.cbits)


    def XOR(self, a, b, output):
        self.qc.cx(a, output)
        self.qc.cx(b, output)


    def Build(self):
        self.PrepareStates()

        for _ in range(2):
            self.Oracle()
            self.qc.barrier()
            self.Diffuser()

        self.Measure()