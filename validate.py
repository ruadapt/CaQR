import sys
from quantum_utils import get_circuit
from qiskit.circuit import Instruction

DEBUG = False

class WireTracker:
    def __init__(self, circuit):
        self.circuit = circuit
        self.wires : list[list] = [[] for _ in range(circuit.num_qubits)]
        self.marker = -1
        for i in range(len(self.wires)):
            self.getCurrentOp(i)
        
    def increment(self):
        if self.marker >= len(self.circuit.data) - 1:
            return False
        self.marker += 1
        dat = self.circuit.data[self.marker]
        instr, quargs, cargs = dat
        qbits = [self.circuit.find_bit(q).index for q in quargs]
        cbits = [self.circuit.find_bit(c).index for c in cargs]
        for index, q in enumerate(qbits):
            self.wires[q].append(((instr, qbits, cbits), index))
        return True

    def getCurrentOp(self, wire):
        if wire >= len(self.wires):
            raise Exception("Not a valid qbit")
        while len(self.wires[wire]) <= 0:
            if not self.increment():
                break
        if len(self.wires[wire]) > 0:
            return self.wires[wire][0]
        return None

    def getNextOp(self, wire):
        if wire >= len(self.wires):
            raise Exception("Not a valid qbit")
        if len(self.wires[wire]) > 0:
            self.wires[wire].pop(0)
        return self.getCurrentOp(wire)

    def getOpFromSubset(self, qbits):
        for q in qbits:
            if self.getCurrentOp(q) == None:
                continue
            op,_ = self.getCurrentOp(q)
            qb = op[1]
            for argindex, qarg in enumerate(qb):
                if self.getCurrentOp(qarg) == None:
                    break
                
                if not op_eq(op, self.getCurrentOp(qarg)[0]) or argindex != self.getCurrentOp(qarg)[1] or qarg not in qbits:
                    break
            else:
                return op
        return None

    def eliminateOp(self, op):
        for i,q in enumerate(op[1]):
            wireop,index = self.getCurrentOp(q)
            if not op_eq(wireop, op):
                raise Exception("Operation elimiation not valid")
            if index != i:
                raise Exception("Operation elimiation not valid")
            self.getNextOp(q)


    def __str__(self) -> str:
        return repr(self.wires)


def map_qubits(qubits : list[int], mapping : dict):
    out = []
    for q in qubits:
        if q not in mapping.keys():
            out.append(q)
        else:
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
    if op1 == None or op2 == None:
        return False
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

    #convert chain to dict
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

    mappingTracker = dict()
    
    visited = set()
    for i,j in chain.items():
        mappingTracker[i] = [i] + j
        visited.add(i)
        for jval in j:
            visited.add(jval)
    for b in range(modified_c.num_qubits):
        if b not in visited:
            mappingTracker[b] = [b]
    def mapping():
        out = dict()
        for i,j in mappingTracker.items():
            out[i] = j[0]
        return out
    
    rev_map = [i for i in range(0, base_c.num_qubits)]
    for i,j in chain.items():
        for k in j:
            rev_map[k] = i

    gt = WireTracker(base_c)
    rt = WireTracker(modified_c)

    x = gt.getOpFromSubset(mapping().values())
    
    while True:
        if x == None:
            break
        (instr, qbit, cbit) = x
        qbit = map_qubits(qbit, mapping())
        
        if DEBUG:
            x_printable = (instr.name, qbit, cbit)

        r_op = None
        for q in qbit:
            rtbit = rev_map[q]
            ptr_op, ptr_index = rt.getCurrentOp(rtbit)
            if not op_eq(x, ptr_op, mapping()) or r_op != None and not op_eq(r_op, ptr_op):
                print("Operation on base does not match modified")
                return False
            if gt.getCurrentOp(q)[1] != ptr_index:
                print("Operation indices on base does not match modified")
                return False
            r_op = ptr_op

        r_op_printable = (r_op[0].name, r_op[1], r_op[2])
        if DEBUG:
            print(f"{x_printable} <--> {r_op_printable}")

        rt.eliminateOp(r_op)
        gt.eliminateOp(x)

        for q in qbit:
            if gt.getCurrentOp(q) == None and len(mappingTracker[rev_map[q]]) > 1:
                rtbit = rev_map[q]

                while True:
                    x,index = rt.getCurrentOp(rtbit)
                    if len(x[1]) != 1 or index != 0:
                        print("Improper gates in modified")
                        return False
                    instr_name = x[0].name
                    if instr_name == 'reset':
                        rt.eliminateOp(x)
                        break
                    if instr_name == 'measure':
                        rt.eliminateOp(x)
                        continue
                    print("Improper gates in modified")
                    return False


                mappingTracker[rtbit].pop(0)
                if DEBUG:
                    print(f"switch {q} to {mappingTracker[rtbit][0]}")
                
        x = gt.getOpFromSubset(mapping().values())
    
    for i in range(gt.circuit.num_qubits):
        if gt.getCurrentOp(i) != None:
            print("Gates in original not addressed (This shouldn't happen)")
            return False
    for i in range(rt.circuit.num_qubits):
        if rt.getCurrentOp(i) != None:
            print("Gates in modified not addressed")
            return False    

    return True

'''
For this current version, there are 2 accepted input schemes:
1 arg: that one arg is used to contruct the filenames for the base circuit, the modified circuit, and the chain file.
3 args: the base circuit, modified circuit, and chain file are given in that order, with exact file paths
'''
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
    result = main(base_filename, reuse_filename, chain_filename)
    if result:
        print("Validation passed")
    else:
        print("Validation failed")