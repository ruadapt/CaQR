import qiskit
import sys
from qiskit import *
from qiskit.visualization.pulse_v2 import draw
from qiskit.visualization import dag_drawer
from qiskit.converters import circuit_to_dag,dag_to_circuit
from qiskit.transpiler import CouplingMap
from qiskit.visualization import plot_histogram
from qiskit.circuit import Reset
from qiskit.circuit.quantumregister import Qubit
from qiskit.circuit.library import Measure

def has_operation_on_qubit(circuit, qubit_index):
    """
    Checks if there is an operation on a specific qubit in the quantum circuit.

    :param QuantumCircuit circuit: The quantum circuit to check.
    :param int qubit_index: The index of the qubit to check for operations.
    :return: True if there is an operation on the qubit, False otherwise.
    """
    for _, qargs, _ in circuit.data:
        if any(qubit.index == qubit_index for qubit in qargs):
            return True
    return False    
            
from qiskit.converters import circuit_to_dag
from qiskit import QuantumCircuit
from qiskit.visualization import dag_drawer

def has_cycle(graph, start, i, j):
    # visited = set()
    # rec_stack = set()

    # Temporarily add the edge from i to j
    if i in graph:
        graph[i].append(j)
    else:
        graph[i] = [j]

    #print(i, j, graph)
    def visit(node):
        visited = set()
        stack = [(start, iter(graph.get(start, [])))]
        while stack:
            node, children = stack[-1]
            if node not in visited:
                visited.add(node)
            try:
                child = next(children)
                if child in visited:
                    # Check if the child is on the current path
                    if any(child == c for c, _ in stack):
                        return True
                else:
                    stack.append((child, iter(graph.get(child, []))))
            except StopIteration:
                stack.pop()
        return False

    cycle_detected = visit(start)

    # Remove the temporarily added edge
    if j in graph[i]:
        graph[i].remove(j)
    if not graph[i]:
        del graph[i]

    return cycle_detected


def share_same_gate(qiskit_dag, i, j):
    for node in qiskit_dag.topological_op_nodes():
        qubits = [qubit.index for qubit in node.qargs]
        if i in qubits and j in qubits:
            return True
    return False

def find_qubit_reuse_pairs(circuit):
    qiskit_dag = circuit_to_dag(circuit)
    # print(qiskit_dag)
    custom_dag = my_custom_dag(circuit)

    num_qubits = len(circuit.qubits)

    reusable_pairs = []

    for i in range(num_qubits):
        last_op_index_i = -1
        for index, (inst, qargs, cargs) in enumerate(circuit.data):
            if any(circuit.find_bit(q).index == i for q in qargs):
                last_op_index_i = index
        for j in range(num_qubits):
            first_op_index_j = -1
            for index, (inst, qargs, cargs) in enumerate(circuit.data):
                if any(circuit.find_bit(q).index == j for q in qargs):
                    first_op_index_j = index
                    break


            if i != j and not share_same_gate(qiskit_dag, i, j) and not has_cycle(custom_dag, last_op_index_i,last_op_index_i,first_op_index_j) and has_operation_on_qubit(circuit,i) and has_operation_on_qubit(circuit,j):
                reusable_pairs.append((i, j))

    return reusable_pairs

def last_index_operation(circuit):
    last_index = {}
    for index, (inst, qargs, cargs) in enumerate(circuit.data):
        for i in range(len(circuit.qubits)):
            if any(circuit.find_bit(q).index == i for q in qargs):
                last_index[i] = index
    return last_index
def first_index_operation(circuit):
    first_index = {}
    for index, (inst, qargs, cargs) in enumerate(circuit.data):
        for i in range(len(circuit.qubits)):
            if any(circuit.find_bit(q).index == i for q in qargs) and i not in first_index:
                first_index[i] = index
    return first_index
    
        
def my_custom_dag(circuit):
    #makes a dag solely using the operation list

    dag = dict()
    vals = dict()
    vals.setdefault(None)
    for index, (inst, qargs, cargs) in enumerate(circuit.data):
        for q in qargs:
            bit = circuit.find_bit(q).index
            if vals.get(bit) != None:
                if dag.get(vals[bit], None) == None:
                    dag[vals[bit]] = []
                dag[vals[bit]].append(index)
            vals[bit] = index
    return dag




# '''
def remove_consecutive_duplicate_gates(circuit):
    """
    Removes consecutive duplicate gates, including measurement gates, from a quantum circuit.

    :param QuantumCircuit circuit: The quantum circuit to modify.
    :return: A new QuantumCircuit with consecutive duplicate gates removed.
    """
    new_circuit = QuantumCircuit(*circuit.qregs, *circuit.cregs)
    prev_inst, prev_qargs, prev_cargs = None, None, None

    for inst, qargs, cargs in circuit.data:
        # Check if the current gate is a duplicate of the previous gate
        if inst == prev_inst and qargs == prev_qargs :
            continue

        new_circuit.append(inst, qargs, cargs)
        prev_inst, prev_qargs, prev_cargs = inst, qargs, cargs

    return new_circuit
# '''
def modify_circuit(circuit, pair):
    """
    Modifies the given circuit by replacing operations on qubit j with qubit i,
    and reordering them to occur after the last use, measurement, and reset of qubit i.

    :param QuantumCircuit circuit: The quantum circuit to modify
    :param tuple pair: A tuple (i, j) indicating the qubits to be swapped
    """
    i, j = pair

    # Ensure the circuit has a classical register for measurement
    if not circuit.cregs:
        circuit.add_register(ClassicalRegister(1))

    # Store all operations, track those that contain j
    operations = []
    check_list = []
    get_list = []
    visited = []
    last_i = -1
    for index, (inst, qargs, cargs) in enumerate(circuit.data):
        operations.append((inst, qargs, cargs))
        visited.append(index)
            
        if any(circuit.find_bit(q).index == i for q in qargs):
            check_list.append(index)
        if any(circuit.find_bit(q).index == j for q in qargs):
            get_list.append(index)

    #generate dag, and reverse it to form dependency lists
    forwards_adjecencies = my_custom_dag(circuit)
    dependencies = [[] for _ in range(len(operations))]
    for a, adj in forwards_adjecencies.items():
        for b in adj:
            dependencies[b].append(a)
    # Create a new circuit with the same registers
    new_circuit = QuantumCircuit(*circuit.qregs, *circuit.cregs)

    # Add all operations to the new circuit that do not depend on j or its descendants
    for index, (inst, qargs, cargs) in enumerate(operations):
        #condition 1 if a dependency has not been processed, condition 2 is if it contains j
        if any(n in visited for n in dependencies[index]) or index in get_list:
            continue
        new_circuit.append(inst, qargs, cargs)
        visited.remove(index)

    #as i should be done, we can do this. If i is not done, something went wrong with i and j
    new_circuit.append(Measure(), [i], [0]).c_if(new_circuit.cregs[0], 1)
    new_circuit.append(Reset(), [i], []).c_if(new_circuit.cregs[0], 1)

    # Process remaining operations, replacing qubit j with qubit i
    for index, (inst, qargs, cargs) in enumerate(operations):
        # print(operations[index])
        if  index in get_list:
            new_qargs = [new_circuit.qubits[i] if circuit.find_bit(q).index == j else q for q in qargs]
            new_circuit.append(inst, new_qargs, cargs)
            visited.remove(index)
        if index in visited:
            new_circuit.append(inst, qargs, cargs)
            visited.remove(index)
    # print(f'there is remain {visited} gates')
    new_circuit = remove_consecutive_duplicate_gates(new_circuit)
    return new_circuit

#I have personally deleted many functions and processes that I have not understood the purpose of, or that I deemed to be incorrect. Feel free to add tham back if the problem demands, as I do not have full scope of the problem.