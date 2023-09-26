import cirq
import numpy as np
from grover_algorithm import GroverAlgorithm


class CirqGrover(GroverAlgorithm):
    clause_list = [[0,1],[0,2],[1,3],[2,3]]
    result_qubit_count = 4
    clause_qubit_count = 4
    output_qubit_count = 1


    def __init__(self):
        self.result_qubits = [
            cirq.LineQubit(i) for i in range(self.result_qubit_count)
        ]
        self.clause_qubits = [
            cirq.LineQubit(i + self.result_qubit_count) 
            for i in range(self.clause_qubit_count)
        ]
        self.output_qubits = [
            cirq.LineQubit(i + self.result_qubit_count + self.clause_qubit_count) 
            for i in range(self.output_qubit_count)
        ]
        self.known_qubits = []
        self.unknown_qubits = [
            qubit for qubit in self.result_qubits
            if qubit not in self.known_qubits
        ]

    def PrepareStates(self):
        initializer = cirq.Circuit()

        # Initialize output in state |->
        initializer.append(cirq.X(*self.output_qubits))
        initializer.append(cirq.H(*self.output_qubits))

        # Initialize results in state |s>
        for result_qubit in self.result_qubits:
            if result_qubit in self.known_qubits:
                initializer.append(cirq.X(result_qubit))
            if result_qubit in self.unknown_qubits:
                initializer.append(cirq.H(result_qubit))

        return initializer

    def Oracle(self):
        oracle_circuit = cirq.Circuit()

        # Compute clauses
        for index, clause in enumerate(self.clause_list):
            qb_a = self.result_qubits[clause[0]]
            qb_b = self.result_qubits[clause[1]]
            self.XOR(oracle_circuit, qb_a, qb_b, self.clause_qubits[index])

        # Flip 'output' bit if all clauses are satisfied
        mct = cirq.ControlledGate(sub_gate=cirq.X, num_controls=4)
        opmct = mct(*self.clause_qubits, self.output_qubits[0])
        oracle_circuit.append(opmct)

        # Uncompute clauses to reset clause-checking bits to 0
        for index, clause in enumerate(self.clause_list):
            qb_a = self.result_qubits[clause[0]]
            qb_b = self.result_qubits[clause[1]]
            self.XOR(oracle_circuit, qb_a, qb_b, self.clause_qubits[index])

        return oracle_circuit


    def XOR(self, circuit: cirq.Circuit, qubit_a, qubit_b, output_qubit):
        circuit.append(cirq.CX(qubit_a, output_qubit))
        circuit.append(cirq.CX(qubit_b, output_qubit))


    def Diffuser(self):
        diffuser = cirq.Circuit()

        # Apply transformation |s> -> |00..0> (H-gates)
        for qubit in self.unknown_qubits:
            diffuser.append(cirq.H(qubit))

        # Apply transformation |00..0> -> |11..1> (X-gates)
        for qubit in self.unknown_qubits:
            diffuser.append(cirq.X(qubit))

        # Do multi-controlled-Z gate
        diffuser.append(cirq.H(self.result_qubits[-1]))

        # multi-controlled-toffoli
        mct_controls = len(self.unknown_qubits) - 1
        mct = cirq.ControlledGate(sub_gate=cirq.X, num_controls=mct_controls)
        opmct = mct(*self.unknown_qubits[:-1], self.result_qubits[-1])
        diffuser.append(opmct)

        diffuser.append(cirq.H(self.result_qubits[-1]))

        # Apply transformation |11..1> -> |00..0>
        for qubit in self.unknown_qubits:
            diffuser.append(cirq.X(qubit))

        # Apply transformation |00..0> -> |s>
        for qubit in self.unknown_qubits:
            diffuser.append(cirq.H(qubit))

        return diffuser

    def Measure(self):
        measurement = cirq.Circuit()
        measurement.append(cirq.measure(*self.result_qubits, key="result"))
        return measurement

    def Build(self):
        full_grover = cirq.Circuit()

        initializer = self.PrepareStates()
        full_grover.append(initializer)

        oracle = self.Oracle()
        diffuser = self.Diffuser()

        for _ in range(2):
            full_grover.append(oracle)
            full_grover.append(diffuser)
            # self.qc.barrier()

        measurement = self.Measure()
        full_grover.append(measurement)

        return full_grover
