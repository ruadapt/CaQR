import qiskit
import sys
from qiskit import *
from qiskit.visualization.pulse_v2 import draw
from qiskit.visualization import dag_drawer
from qiskit.converters import circuit_to_dag,dag_to_circuit
from qiskit.transpiler import CouplingMap
from qiskit.visualization import plot_histogram
import networkx as nx
# Here is a simplified version of the Union-Find algorithm using functions

def find(x, parent):
    """ Function to find the leader (representative) of the set that x belongs to. """
    if parent[x] != x:
        parent[x] = find(parent[x], parent)  # Path compression
    return parent[x]

def union(x, y, parent):
    """ Function to perform the union of two sets x and y. """
    x_root = find(x, parent)
    y_root = find(y, parent)
    if x_root != y_root:
        parent[y_root] = x_root  # Merge y into x

def union_find(map):
    """ Function to perform union-find on a map. """
    parent = {i: i for i in map}  # Initialize parent for each node
    # print(parent)
    # Initialize all nodes and perform union operations
    for leader in map:
        for follower in map[leader]:
            parent.setdefault(follower, follower)  # Ensure follower is in parent map
            union(leader, follower, parent)
    # print(parent)
    # Create groups with the leaders
    # print(map)
    groups = {}
    for leader in map:
        # Find the ultimate leader (parent) for each group
        leader_parent = find(leader, parent)
        groups[leader_parent] = set()

    # Add nodes to their respective groups based on the ultimate leader
    for follower in parent:

        follower_parent = find(follower, parent)
        if follower_parent in groups and follower_parent != follower:
            # print(follower_parent, follower)
            groups[follower_parent].add(follower)
            
    return groups

def get_circuit(name):
    qc = QuantumCircuit.from_qasm_file(f'{name}')
    circuit = qiskit.QuantumCircuit.from_qasm_file(f'{name}')
    return qc
def output_qasm(circuit, input_argument,map):
    result_groups = union_find(map)
    map = result_groups
    # benchmakrs/ .qasm
    modified_name = input_argument.split("/")
    nn = modified_name[1].split(".")
    # print(nn[0])
    with open(f"output/{nn[0]}_reuse.qasm", "w") as file:
        file.write(circuit.qasm())
    with open(f"output/{nn[0]}_reuse_map.txt", "w+") as file:
        for m in map:
            file.write(f"{m} : ")
            s1 = "{ "
            for n in map[m]:
                s1 += f"  {n} ,"
            s1 = s1[:-2]
            s1 += " }"
            file.write(s1)
            # print(s1)
            file.write("\n")
    with open(f"output/{nn[0]}_reuse_chain.txt", "w") as file:
        for m in map:
            file.write(f"{m} ")
            for n in map[m]:
                file.write(f" -> {n} ")
            file.write("\n")
        # file.write(str(map))
    
    
    
    




