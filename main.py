from qiskit import QuantumCircuit
from circuit_analysis import find_qubit_reuse_pairs
from circuit_analysis import modify_circuit
from qiskit.test.mock import FakeMumbai
from quantum_utils import get_circuit
from quantum_utils import output_qasm
import sys

def main():

    
    backend = FakeMumbai()
    # Example usage
    
    # Example of reading a command line argument
    if len(sys.argv) > 1:
        input_argument = sys.argv[1]
        print(input_argument)
    else:
        print("Sorry, no file input is given")
        sys.exit(1)  # Exits the program with an error code (1)

    qc = get_circuit(input_argument)
    # qc = QuantumCircuit(5)
    # for k in range(5):
    #     qc.h(k)
    # for k in range(4):
    #     qc.cx(k, 4)
    # for k in range(5):
    #     qc.h(k)
    reuse_pairs = find_qubit_reuse_pairs(qc)
    print(qc)
    iter = 0
    cur_qc = qc.copy() 
    while len(reuse_pairs) > 0 and iter < len(qc.qubits) - 1:
        print(reuse_pairs)
        depth_diff = sys.maxsize
        
        # for i in range(len(reuse_pairs)):
        #     test_qc = cur_qc.copy() 
        #     test_out_qc = modify_circuit(test_qc, reuse_pairs[i])
        #     if test_out_qc.depth() - cur_qc.depth() < depth_diff:
        #         depth_diff = test_out_qc.depth() - qc.depth()
        #         best_pair = reuse_pairs[i]
        
        # print(f"Best pair: {best_pair}")
        # print(cur_qc)
        modified_qc = modify_circuit(cur_qc,reuse_pairs[0])
        print(modified_qc)
        reuse_pairs = find_qubit_reuse_pairs(modified_qc)
        cur_qc  = modified_qc.copy() 
        iter += 1
    print(f"We reuse {iter} qubits, now the logical qubits needed are: {len(qc.qubits)-iter}")
    output_qasm(cur_qc, input_argument)

if __name__ == '__main__':
    main()

