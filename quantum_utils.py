import qiskit
import sys
from qiskit import *
from qiskit.visualization.pulse_v2 import draw
from qiskit.visualization import dag_drawer
from qiskit.converters import circuit_to_dag,dag_to_circuit
from qiskit.transpiler import CouplingMap
from qiskit.visualization import plot_histogram
from qiskit.providers.aer.noise import NoiseModel
import networkx as nx
import networkx as nx

def get_circuit(name):
    qc = QuantumCircuit.from_qasm_file(f'benchmarks\{name}.qasm')
    # circuit = qiskit.QuantumCircuit.from_qasm_file(f'{name}')
    return qc
def output_qasm(circuit, input_argument):
    with open(f"output\{input_argument}_reuse.qasm", "w") as file:
        file.write(circuit.qasm())
    
    
    
    




