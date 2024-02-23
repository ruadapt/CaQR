import sys
from quantum_utils import get_circuit

class WireTracker:
    def __init__(self, circuit):
        self.circuit = circuit
        self.wires = [[] for _ in range(circuit.num_qubits)]
        self.marker = -1

    def getNext(self, wire):
        if wire >= len(self.wires):
            raise Exception("What in tarnation")
        while len(self.wires[wire]) <= 0 and self.marker < len(self.circuit.data) - 1:
            self.marker += 1
            dat = self.circuit.data[self.marker]
            inst, quargs, _ = dat
            for index, q in enumerate(quargs):
                self.wires[self.circuit.find_bit(q).index].append((dat, index))

        if len(self.wires[wire]) <= 0:
            return None
        return self.wires[wire].pop(0)

    def __str__(self) -> str:
        return repr(self.wires)



def main():
    bm = sys.argv[1]
    base_c = get_circuit(f"benchmarks/{bm}.qasm")
    modified_c = get_circuit(f"output/{bm}_reuse.qasm")
    chain = {}
    for line in open(f"output/{bm}_reuse_chain.txt"):
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

    gt = WireTracker(base_c)
    l = []
    while True:
        x = gt.getNext(0)
        if x == None:
            break
        (instr, _, _), index = x
        l.append((instr.name, index))
    print(l)

    #print(base_c)




if __name__ == "__main__":
    main()