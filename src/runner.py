import argparse
import time
import datetime

from qiskit_aer import AerSimulator
from qiskit import Aer, transpile
import qsimcirq

from qiskit_grover import QiskitGrover
from cirq_grover import CirqGrover

SHOTS = 4096

def main():
    parser = argparse.ArgumentParser(description="Quantum Simulator Selector")

    # Add a flag for selecting the running environment (laptop or pakhus)
    parser.add_argument('-e', '--environment', choices=['laptop', 'pakhus'], required=True,
                        help='Specify the environment (laptop or pakhus)')
    
    # Add a flag for selecting the quantum simulator (qiskit or cirq)
    parser.add_argument('-s', '--simulator', choices=['qiskit', 'cirq'], required=True, 
                        help='Select the quantum simulator (qiskit or cirq)')
    
    # Add a flag for specifying the number of threads (1 or 8)
    parser.add_argument('-t', '--threads', type=int, choices=[1, 8], required=True,
                        help='Specify the number of threads (1 or 8)')
    
    args = parser.parse_args()
    
    # Access the selected options
    selected_simulator = args.simulator
    num_threads = args.threads
    environment = args.environment
    timestamp = datetime.datetime.utcnow().isoformat()
    time = 0
    if selected_simulator == "qiskit":
        time = qiskit_run(num_threads)
    elif selected_simulator == "cirq":
        time = cirq_run(num_threads)

    print(f"{timestamp}, {environment}, {selected_simulator}, {num_threads}, {time}")
    

def qiskit_run(threads):
    grover = QiskitGrover()
    grover.Build()
    qc = grover.qc
    aer_simulator = AerSimulator()
    aer_simulator.set_options(
        method = "statevector",
        max_parallel_threads = threads,
        max_parallel_experiments = threads,
        max_parallel_shots = threads,
        statevector_parallel_threshold = 1
    )
    transpiled_qc = transpile(qc, aer_simulator)

    start_time = time.time()
    
    aer_simulator.run(transpiled_qc, shots=SHOTS)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    return elapsed_time

def cirq_run(threads):
    grover = CirqGrover()
    qc = grover.Build()
    
    options = {'cpu_threads': threads}
    qsim_simulator = qsimcirq.QSimSimulator(options)

    start_time = time.time()
    qsim_simulator.run(qc, repetitions=SHOTS)
    end_time = time.time()
    elapsed_time = end_time - start_time

    return elapsed_time


if __name__ == '__main__':
    main()
