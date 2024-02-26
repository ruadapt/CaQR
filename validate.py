import sys
from quantum_utils import get_circuit
from qiskit.circuit import Instruction

class WireTracker:
    def __init__(self, circuit):
        self.circuit = circuit
        self.wires : list[list] = [[] for _ in range(circuit.num_qubits)]
        self.marker = -1

    def getNext(self, wire):
        if wire >= len(self.wires):
            raise Exception("Not a valid qbit")
        while len(self.wires[wire]) <= 0 and self.marker < len(self.circuit.data) - 1:
            self.marker += 1
            dat = self.circuit.data[self.marker]
            instr, quargs, cargs = dat
            qbits = [self.circuit.find_bit(q).index for q in quargs]
            cbits = [self.circuit.find_bit(c).index for c in cargs]
            for index, q in enumerate(qbits):
                self.wires[q].append(((instr, qbits, cbits), index))

        if len(self.wires[wire]) <= 0:
            return None
        return self.wires[wire].pop(0)

    def __str__(self) -> str:
        return repr(self.wires)


def map_qubits(qubits : list[int], mapping : list[int]):
    out = []
    for q in qubits:
        if q >= len(mapping):
            raise Exception("Qubit out of range")
        out.append(mapping[q])
    return out

def list_eq(arr1 : list, arr2 : list):
    count = 0
    for i,j in zip(arr1, arr2):
        count += 1
        if i != j:
            return False
    return count == len(arr1) == len(arr2)

def op_eq(op1 : tuple[Instruction,list[int],list[int]], op2 : tuple[Instruction,list[int],list[int]], map_over_2 = None):
    if op1[0].name != op2[0].name:
        return False
    if op1[0].num_qubits != op2[0].num_qubits:
        return False
    if op1[0].num_qubits != op2[0].num_qubits:
        return False
    if not list_eq(op1[0].params, op2[0].params):
        return False
    if map_over_2:
        if not list_eq(op1[1], map_qubits(op2[1], map_over_2)):
            return False
    else:
        if not list_eq(op1[1], op2[1]):
            return False
    if not list_eq(op1[2], op2[2]):
        return False
    return True

def main(base_filename, reuse_filename, chain_filename):
    
    base_c = get_circuit(base_filename)
    modified_c = get_circuit(reuse_filename)
    chain = {}
    for line in open(chain_filename):
        base = None
        contChain = False
        for term in line.split():
            if term == '->':
                contChain = True
                continue
            if contChain:
                chain[base].append(int(term))
            else:
                base = int(term)
                chain[base] = []
            contChain = False

    mapping = [i for i in range(base_c.num_qubits)]
    for k,v in chain.items():
        for i in v:
            mapping[i] = k
    print(mapping)

    #testing

    gt = WireTracker(base_c)
    l = []
    l2 = []
    while True:
        x = gt.getNext(0)
        if x == None:
            break
        (instr, qbit, cbit), index = x
        l.append(((instr, qbit, cbit), index))
        qbit = map_qubits(qbit, mapping)
        l2.append(((instr, qbit, cbit), index))
    print(l, "\n", l2)
    
    return True



if __name__ == "__main__":
    if len(sys.argv) == 2:
        bm = sys.argv[1]
        base_filename = f"benchmarks/{bm}.qasm"
        reuse_filename = f"output/{bm}_reuse.qasm"
        chain_filename = f"output/{bm}_reuse_chain.txt"
    elif len(sys.argv) == 4:
        base_filename = sys.argv[1]
        reuse_filename = sys.argv[2]
        chain_filename = sys.argv[3]
    else:
        raise Exception("Invalid Argument Count")
    main(base_filename, reuse_filename, chain_filename)