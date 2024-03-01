from qiskit import QuantumCircuit
from circuit_analysis import find_qubit_reuse_pairs
from circuit_analysis import modify_circuit
from circuit_analysis import last_index_operation
from circuit_analysis import first_index_operation
# from qiskit.test.mock import FakeMumbai
from quantum_utils import get_circuit
from quantum_utils import output_qasm
import argparse
import sys
import copy

def main():

    
    # backend = FakeMumbai()
    # Example usage
    parser = argparse.ArgumentParser(description="Qubit reuse pair finder")
    parser.add_argument('-b','--benchmark', type=str, help="Path to the QASM file")
    parser.add_argument('-v', '--verbose', type=int, default=0,
                        help="Verbosity level (default: 0)")
    parser.add_argument('-w', '--weight', type=tuple, default=(1,1,1),
                        help="weight for the depth difference (default: 0)")

    args = parser.parse_args()
    input_argument = args.benchmark
    qc = get_circuit(input_argument)
    # qc = QuantumCircuit(5)
    # for k in range(5):
    #     qc.h(k)
    # for k in range(4):
    #     qc.cx(k, 4)
    # for k in range(5):
    #     qc.h(k)
    reuse_pairs = find_qubit_reuse_pairs(qc)
    if args.verbose > 0:
        print(qc)
    iter = 0
    cur_qc = qc.copy() 
    chain = []
    while len(reuse_pairs) > 0 and iter < len(qc.qubits) - 1:
        if args.verbose > 0:
            print(reuse_pairs)
        depth_diff = sys.maxsize
        lst_index = last_index_operation(cur_qc)
        fst_index = first_index_operation(cur_qc)
        if args.verbose > 0:
            print(lst_index)
            print(fst_index)
        for i in range(len(reuse_pairs)):
            test_qc = cur_qc.copy() 
            test_out_qc = modify_circuit(test_qc, reuse_pairs[i])
            
            if args.weight[0]*(test_out_qc.depth() - cur_qc.depth()) + args.weight[1]*lst_index[reuse_pairs[i][0]]+args.weight[2]*abs(lst_index[reuse_pairs[i][0]] - fst_index[reuse_pairs[i][1]]) < depth_diff:
                depth_diff = test_out_qc.depth() - qc.depth() + 0.5*lst_index[reuse_pairs[i][1]]
                best_pair = reuse_pairs[i]
        if args.verbose > 0:
            print(f"Best pair: {best_pair}")
        chain.append((best_pair[0],best_pair[1]))
        
        modified_qc = modify_circuit(cur_qc,best_pair)
        if (args.verbose > 0) :
            print(modified_qc)
        reuse_pairs = find_qubit_reuse_pairs(modified_qc)
        cur_qc  = modified_qc.copy()
        iter += 1
    lst_index = last_index_operation(cur_qc)

    # print(chain)
    marked = set()
    heads = set()
    map_pre = {}
    for start, end in chain:
        if start in map_pre:
            map_pre[start].append(end)
        else:
            map_pre[start] = [end]
            if start not in marked:
                heads.add(start)
        if end in heads:
            heads.remove(end)
        marked.add(end)
    #print(map_pre)
    
    map_post = {}
    for h in heads:
        map_post[h] = []
        stack = list(reversed(map_pre[h]))
        while len(stack) > 0:
            node = stack.pop()
            map_post[h].append(node)
            if node in map_pre:
                stack.extend(reversed(map_pre[node]))
    #print(map_post)
    
    # out put the map to a txt file

    print(f"We reuse {iter} qubits, and now a total of {len(lst_index)} logical qubits are used.")
    output_qasm(cur_qc, input_argument,map_post)
    # add the weight as a parameter.  
    # output the qubit chain with list<list> output as txt file

if __name__ == '__main__':
    main()
