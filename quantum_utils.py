import qiskit
import sys
from qiskit import *
from qiskit.visualization.pulse_v2 import draw
from qiskit.visualization import dag_drawer
from qiskit.converters import circuit_to_dag,dag_to_circuit
from qiskit.transpiler import CouplingMap
from qiskit.visualization import plot_histogram
import networkx as nx
import networkx as nx

def get_circuit(name):
    qc = QuantumCircuit.from_qasm_file(f'{name}')
    circuit = qiskit.QuantumCircuit.from_qasm_file(f'{name}')
    return qc
def output_qasm(circuit, input_argument):
    # benchmakrs/ .qasm
    modified_name = input_argument.split("/")
    nn = modified_name[1].split(".")
    print(nn[0])
    with open(f"output/{nn[0]}_reuse.qasm", "w") as file:
        file.write(circuit.qasm())
    
    
    
    




