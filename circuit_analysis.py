import qiskit
import sys
from qiskit import *
from qiskit.visualization.pulse_v2 import draw
from qiskit.visualization import dag_drawer
from qiskit.converters import circuit_to_dag,dag_to_circuit
from qiskit.transpiler import CouplingMap
from qiskit.visualization import plot_histogram
from qiskit.providers.aer.noise import NoiseModel
from qiskit.circuit import Reset
import networkx as nx
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
from qiskit.circuit.quantumregister import Qubit
from qiskit.circuit.library import Measure

def find_all_conflict(i,cur_index,dep_info):
    res_set = []
    #print(cur_index)
    while cur_index > 0:
        candidate = []
        for pair in dep_info[cur_index]:
            if pair[0] == i and pair[1] not in candidate:
                candidate.append(pair[1])
            if pair[1] == i and pair[0] not in candidate:
                candidate.append(pair[0])
        for c in candidate:
            res_set.append(c)
            return_set = find_all_conflict(c,cur_index-1,dep_info)
            for r in return_set:
                if r not in res_set:
                    res_set.append(r)
        cur_index = cur_index - 1
    return res_set
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
    
def greedy_find(qc):
    
    dag_qc_r = circuit_to_dag(qc)
    layer = dag_qc_r.layers()
    cur_index = 0
    qubits_start_layer = [-1]*len(qc.qubits)
    qubits_end_layer = [-1]*len(qc.qubits)
    dependency = {}
    dep_index = {}
    pre_dependency = {}
    for i in range(len(qc.qubits)):
        dependency[i] = []
    
    for i in layer:
        list_node = i['graph'].op_nodes()
        # print(f"start new layer {cur_index}:")
        # print("******")
        #print(list_node)
        pre_dependency[cur_index] = []
        for cur_node in list_node:
            if len(cur_node.qargs) > 1:
                control_q = cur_node.qargs[0].index
                target_q = cur_node.qargs[1].index
                #print(f"the {cur_node.name} gate with control qubit {cur_node.qargs[0].index} target qubit {cur_node.qargs[1].index} ")
                if qubits_start_layer[control_q] == -1:
                    qubits_start_layer[control_q] = cur_index
                if qubits_start_layer[target_q] == -1:
                    qubits_start_layer[target_q] = cur_index
                qubits_end_layer[control_q] = cur_index
                qubits_end_layer[target_q] = cur_index
                dependency[control_q].append(target_q)
                dependency[target_q].append(control_q)
                pre_dependency[cur_index].append([control_q,target_q])
                pre_dependency[cur_index].append([target_q,control_q])
                dep_index[(control_q,target_q)] = cur_index
                dep_index[(target_q,control_q)] = cur_index
                    
            else:
                control_q = cur_node.qargs[0].index
                #print(f"the {cur_node.name} gate with control qubit {cur_node.qargs[0].index} ")
                if qubits_start_layer[control_q] == -1:
                    qubits_start_layer[control_q] = cur_index
                qubits_end_layer[control_q] = cur_index
                    
        cur_index+=1
    qubits_start_layer_res  = [i for i in qubits_start_layer if i != -1]
    qubits_end_layer_res  = [i for i in qubits_end_layer if i != -1]
    
    #print(f"the qubits start time is {qubits_start_layer_res}")
    #print(f"the qubits end time is {qubits_end_layer_res}")
    count = 0 
    res_pair = []
    conflict_p = {}
    for i in range(len(qubits_start_layer_res)):
        conflict_p[i] = []
    #print(f"the dependency information is {pre_dependency}")
    #print(f"the last gate index information is {dep_index}")
    #? we start with i and find all not possible j pairs, so the rest will be our result
    for i in range(len(qubits_start_layer_res)):
        for j in range(len(qubits_end_layer_res)):
            if i!=j and j in dependency[i]:
                cur_index = dep_index[(i,j)]
                #print(f'we find the {i}, {j} at layer {cur_index}')
                all_conflict_pairs = find_all_conflict(i,cur_index,pre_dependency)
                #print(f'the qubit {i} has conflict with {all_conflict_pairs}')
                for ap in all_conflict_pairs:
                    if ap not in conflict_p[i]:
                        conflict_p[i].append(ap)
                #count += 1
                #res_pair.append([i,j])
    for i in range(len(qubits_start_layer_res)):
        for j in range(len(qubits_end_layer_res)):
            # if i!=j and j not in conflict_p[i] and has_operation_on_qubit(qc, i) and has_operation_on_qubit(qc, j):
            if i!=j and j not in conflict_p[i]:
                count += 1
                res_pair.append([i,j])
    #print(dependency)
    #print(res_pair)
    
    return count,res_pair

    
    
    return res_list
def cost_function(qc,res_pair,backend):
    cost_pair = {}
    res_list = []
    for r in res_pair:
        #print(f"the reuse pairs are {r}")
        #! if we want to reuse this pair r[0] and r[1]  
        cg = backend.configuration()
        cm = cg.to_dict()['coupling_map']
        cm = CouplingMap(cm)
        dag_qc_r = circuit_to_dag(qc)
        layer = dag_qc_r.layers()
        total_score = 0
        for i in layer:
            list_node = i['graph'].op_nodes()
            for cur_node in list_node:
                if len(cur_node.qargs) > 1:
                    control_q = cur_node.qargs[0].index
                    target_q = cur_node.qargs[1].index
                    #print(f"the {cur_node.name} gate with control qubit {cur_node.qargs[0].index} target qubit {cur_node.qargs[1].index} ")
                    if control_q == r[0]:
                        pre_distance = CouplingMap.distance(cm,control_q,target_q)
                        post_distance = CouplingMap.distance(cm,r[1],target_q)
                        cost = post_distance-pre_distance
                        total_score += cost
                    if target_q == r[0]:
                        pre_distance = CouplingMap.distance(cm,control_q,target_q)
                        post_distance = CouplingMap.distance(cm,control_q,r[1])
                        cost = post_distance-pre_distance
                        total_score += cost
        temp = ','.join([str(tt) for tt in r])
        cost_pair[temp] = total_score  
        #print(f" if we use the {r} the total cost is {total_score}") 
        sort_pair = dict(sorted(cost_pair.items(), key=lambda item: item[1]))
        rep_check = []
        res_list = []
        for k,v in sort_pair.items():
            temp_list = k.split(',')
            if int(temp_list[1]) not in rep_check and int(temp_list[0]) not in rep_check:
                res_list.append([int(temp_list[0]),int(temp_list[1])])
                rep_check.append(int(temp_list[0]))
                rep_check.append(int(temp_list[1]))

    
        #print(res_list)       
    return res_list
def modified_circuit(qc,res_pair,k):
    register_name = ['aa','bb','cc','dd','ee','ff']
    qc_qasm = qc.qasm()
    qc_qasm_list = qc_qasm.split('\n')
    k = min(len(res_pair),k)
    #print(k)
    output=[]
    reuse =[]
    for i in range(k):
        #print(f'we will reuse qubit {res_pair[i]}')
        
        a = res_pair[i][1]
        b =res_pair[i][0]
        output=[]
        reuse =[]
        for cur_qasm in qc_qasm_list:
            if f'[{a}]' in cur_qasm and 'creg' not in cur_qasm:
                temp_str = cur_qasm.replace(f'[{a}]',f'[{b}]')
                reuse.append(temp_str)
            else:
                ##? replace the 2 to 0
                output.append(cur_qasm)
        
        output.insert(3,f'creg {register_name[i]}[1];')
        output.append(f'measure q[{b}] -> {register_name[i]}[0];')
        output.append(f'if ({register_name[i]} == 1) x q[{b}];')
        qc_qasm_list.clear()
        for i in output:
            qc_qasm_list.append(i)
        for i in reuse:
            qc_qasm_list.append(i)
        #print(qc_qasm_list)
         
    with open ('benchreuse.qasm','w+') as f:
        for line in output:
            f.write(line)
            f.write('\n')
        for line in reuse:
            f.write(line)
            f.write('\n')
    return qc 
            
        

def find_qubit_reuse_pairs(circuit):
    # Convert the circuit to a DAG
    dag = circuit_to_dag(circuit)
    
    # Get the total number of qubits
    num_qubits = circuit.num_qubits
    
    # List to store pairs of reusable qubits
    reusable_pairs = []

    # Check each pair of qubits
    for i in range(num_qubits):
        for j in range(num_qubits):
            if i != j:
                # Check if there is no direct gate between q_i and q_j
                no_direct_gate = True
                for node in dag.op_nodes():
                    qubits = [qubit.index for qubit in node.qargs]
                    if i in qubits and j in qubits:
                        no_direct_gate = False
                        break

                # Check if reusing q_i as q_j does not form a cycle
                # This is a simplified check assuming the circuit follows the conditions described
                if no_direct_gate:
                    if i < j and has_operation_on_qubit(circuit,i) and has_operation_on_qubit(circuit,j):  # Assuming gates are applied in order and q_i is reused as q_j only if i < j
                        reusable_pairs.append((i, j))

    return reusable_pairs

# Example usage
# qc2 = QuantumCircuit(4)
# qc2.cx(0,3)
# qc2.cx(1, 3)
# qc2.cx(2,3)

# reuse_pairs = find_qubit_reuse_pairs(qc2)
# reuse_pairs






def remove_idle_qwires(circ):
    dag = circuit_to_dag(circ)

    idle_wires = list(dag.idle_wires())
    for w in idle_wires:
        dag._remove_idle_wire(w)
        dag.qubits.remove(w)

    dag.qregs = OrderedDict()

    return dag_to_circuit(dag)

    return new_qc
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
        if inst == prev_inst and qargs == prev_qargs and cargs == prev_cargs:
            continue

        new_circuit.append(inst, qargs, cargs)
        prev_inst, prev_qargs, prev_cargs = inst, qargs, cargs

    return new_circuit
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

    # Store all operations and find the last operation involving qubit i
    operations = []
    check_list = []
    get_list = []
    last_op_index_i = -1
    for index, (inst, qargs, cargs) in enumerate(circuit.data):
        operations.append((inst, qargs, cargs))
        if any(circuit.find_bit(q).index == i for q in qargs):
            check_list.append(index)
            last_op_index_i = index
        if any(circuit.find_bit(q).index == j for q in qargs):
            get_list.append(index)
            

    # Create a new circuit with the same registers
    new_circuit = QuantumCircuit(*circuit.qregs, *circuit.cregs)

    # Add operations up to the last operation of qubit i
    for index, (inst, qargs, cargs) in enumerate(operations):
        # if isinstance(inst, Measure) and any(circuit.find_bit(q).index == j for q in qargs):
        #     continue
        if index <= last_op_index_i and all(circuit.find_bit(q).index != j for q in qargs):
            new_circuit.append(inst, qargs, cargs)
        if index == last_op_index_i:
            # Insert measurement and reset for qubit i
            new_circuit.measure(i, 0)
            new_circuit.append(Reset(), [i], []).c_if(new_circuit.cregs[0], 1)
            
    # print(check_list)
    # for index, (inst, qargs, cargs) in enumerate(operations):
    #     if index <= last_op_index_i and all(circuit.find_bit(q).index == j for q in qargs):
    #         new_qargs = [new_circuit.qubits[i] if circuit.find_bit(q).index == j else q for q in qargs]
    #         new_circuit.append(inst, new_qargs, cargs)
        

    # Process remaining operations, replacing qubit j with qubit i
    for index, (inst, qargs, cargs) in enumerate(operations):
        # print(operations[index])
        if isinstance(inst, Measure) and any(circuit.find_bit(q).index == j for q in qargs):
            continue
        if  index in get_list:
            new_qargs = [new_circuit.qubits[i] if circuit.find_bit(q).index == j else q for q in qargs]
            new_circuit.append(inst, new_qargs, cargs)

    return remove_consecutive_duplicate_gates(new_circuit)