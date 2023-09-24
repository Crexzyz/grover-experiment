import cirq
from grover_algorithm import GroverAlgorithm


class CirqGrover(GroverAlgorithm):
    clause_list = [[0,1],[0,2],[1,3],[2,3]]


    def __init__(self):
        self.result_qubits = [cirq.LineQubit(i) for i in range(4)]
        self.clause_qubits = [cirq.LineQubit(i + 4) for i in range(4)]
        self.output_qubits = [cirq.LineQubit(i + 4 + 4) for i in range(1)]

    def PrepareStates(self):
        pass

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
        pass

    def Measure(self):
        pass

    def Build(self):
        pass
